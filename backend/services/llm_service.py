
import os
import time
import logging

from dotenv import load_dotenv
from google import genai


load_dotenv()

logger = logging.getLogger(__name__)


class LLMService:
    """
    Gemini LLM service with retry handling and configurable model fallback.

    Environment variables:
        GEMINI_API_KEY:
            Your Gemini API key.

        GEMINI_MODEL:
            Primary model to use.

        GEMINI_FALLBACK_MODELS:
            Optional comma-separated list of fallback models.

        GEMINI_MAX_RETRIES:
            Number of retries for temporary failures.
    """

    RETRYABLE_STATUS_CODES = {
        429,  # Resource exhausted / rate limit
        500,  # Internal server error
        502,  # Bad gateway
        503,  # Service unavailable
        504,  # Gateway timeout
    }

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        ).strip()

        fallback_models = os.getenv(
            "GEMINI_FALLBACK_MODELS",
            "",
        )

        self.fallback_models = [
            model.strip()
            for model in fallback_models.split(",")
            if model.strip()
        ]

        # Remove duplicates and prevent the primary model from
        # appearing in the fallback list.
        self.fallback_models = list(
            dict.fromkeys(
                model
                for model in self.fallback_models
                if model != self.model
            )
        )

        self.max_retries = int(
            os.getenv("GEMINI_MAX_RETRIES", "3")
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. "
                "Please add it to your .env file."
            )

        self.client = genai.Client(
            api_key=api_key,
        )

    # --------------------------------------------------
    # ERROR HANDLING
    # --------------------------------------------------

    def _get_status_code(self, error):
        """
        Extract the HTTP status code from a Gemini SDK exception.
        """

        status_code = getattr(
            error,
            "code",
            None,
        )

        if status_code is None:
            status_code = getattr(
                error,
                "status_code",
                None,
            )

        try:
            return int(status_code)
        except (TypeError, ValueError):
            return None

    def _is_retryable(self, error):
        """
        Return True only for temporary API failures.
        """

        status_code = self._get_status_code(error)

        if status_code in self.RETRYABLE_STATUS_CODES:
            return True

        # Some SDK/network errors do not expose an HTTP status code.
        error_name = error.__class__.__name__.lower()

        if any(
            name in error_name
            for name in (
                "timeout",
                "connection",
                "temporarily",
            )
        ):
            return True

        return False

    def _wait_before_retry(self, retry_number):
        """
        Exponential backoff: 2, 4, 8, ... seconds.
        """

        delay = min(
            2 ** retry_number,
            30,
        )

        logger.warning(
            "Gemini request failed temporarily. "
            "Retrying in %s seconds...",
            delay,
        )

        time.sleep(delay)

    # --------------------------------------------------
    # NON-STREAMING RESPONSE
    # --------------------------------------------------

    def generate_response(self, prompt):

        models_to_try = [
            self.model,
            *self.fallback_models,
        ]

        last_error = None

        for model_index, model_name in enumerate(models_to_try):

            for retry_number in range(self.max_retries + 1):

                try:

                    logger.info(
                        "Sending request to Gemini model: %s",
                        model_name,
                    )

                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )

                    return response.text or ""

                except Exception as error:

                    last_error = error

                    if not self._is_retryable(error):

                        logger.exception(
                            "Non-retryable Gemini error."
                        )

                        raise

                    if retry_number < self.max_retries:

                        self._wait_before_retry(
                            retry_number + 1
                        )

                    else:

                        logger.warning(
                            "Model %s failed after retries.",
                            model_name,
                        )

            # The primary model has failed all retries.
            # Continue with the next configured fallback model.
            if model_index < len(models_to_try) - 1:

                logger.warning(
                    "Switching from model %s to fallback model %s.",
                    model_name,
                    models_to_try[model_index + 1],
                )

        # All configured models failed.
        raise RuntimeError(
            "StudyMate could not get a response from Gemini. "
            "The configured models may be temporarily unavailable. "
            "Please try again later."
        ) from last_error

    # --------------------------------------------------
    # STREAMING RESPONSE
    # --------------------------------------------------

    def generate_response_stream(self, prompt):

        models_to_try = [
            self.model,
            *self.fallback_models,
        ]

        last_error = None

        for model_index, model_name in enumerate(models_to_try):

            for retry_number in range(self.max_retries + 1):

                emitted_text = False

                try:

                    logger.info(
                        "Starting Gemini stream with model: %s",
                        model_name,
                    )

                    response_stream = (
                        self.client.models.generate_content_stream(
                            model=model_name,
                            contents=prompt,
                        )
                    )

                    for chunk in response_stream:

                        if chunk.text:

                            emitted_text = True
                            yield chunk.text

                    return

                except Exception as error:

                    last_error = error

                    # Once text has been sent to the UI, restarting
                    # with another model could duplicate the answer.
                    if emitted_text:
                        raise

                    if not self._is_retryable(error):
                        raise

                    if retry_number < self.max_retries:

                        self._wait_before_retry(
                            retry_number + 1
                        )

                    else:

                        logger.warning(
                            "Streaming model %s failed after retries.",
                            model_name,
                        )

            if model_index < len(models_to_try) - 1:

                logger.warning(
                    "Switching streaming request from %s to %s.",
                    model_name,
                    models_to_try[model_index + 1],
                )

        raise RuntimeError(
            "StudyMate could not stream a response from Gemini. "
            "The configured models may be temporarily unavailable. "
            "Please try again later."
        ) from last_error
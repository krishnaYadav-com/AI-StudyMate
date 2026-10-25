import re

from backend.services.llm_service import LLMService
from backend.services.document_service import DocumentService
from backend.tools.calculator import Calculator


class StudyMateAgent:

    def __init__(self):

        self.llm = LLMService()

        self.document_service = DocumentService()

        self.calculator = Calculator()

    # --------------------------------------------------
    # CONVERSATION HISTORY
    # --------------------------------------------------

    def _get_history_text(self, history):

        # Use only the last 4 messages.
        recent_history = history[-4:]

        formatted_history = []

        for message in recent_history:

            role = message["role"]

            # Limit the length of each message.
            content = message["content"][:1000]

            formatted_history.append(
                f"{role.upper()}: {content}"
            )

        return "\n".join(
            formatted_history
        )

    # --------------------------------------------------
    # CALCULATOR
    # --------------------------------------------------

    def _is_calculation(self, query):

        query = query.lower()

        keywords = [
            "calculate",
            "what is",
            "how much",
            "multiply",
            "divide",
            "addition",
            "subtract"
        ]

        return any(
            keyword in query
            for keyword in keywords
        )

    def _extract_expression(self, query):

        query = query.replace(",", "")

        match = re.search(
            r"[-+]?\d+(?:\.\d+)?"
            r"(?:\s*[*+\-/%%^]\s*[-+]?\d+(?:\.\d+)?)+",
            query
        )

        if not match:
            return None

        expression = match.group(0)

        expression = expression.replace(
            "^",
            "**"
        )

        return expression

    # --------------------------------------------------
    # CHAT PROMPT
    # --------------------------------------------------

    def _build_chat_prompt(
        self,
        query,
        history,
        document_chunks=None
    ):

        document_context = ""

        if document_chunks:

            document_context = (
                self.document_service.search_documents(
                    query,
                    document_chunks,
                    top_k=2
                )
            )

        history_text = self._get_history_text(
            history
        )

        prompt = f"""
You are AI StudyMate, an intelligent
academic study assistant.

Your objective is to help students
understand academic concepts.

Instructions:

1. Explain concepts in simple language.
2. Use examples wherever appropriate.
3. Be accurate and educational.
4. Use the conversation history to
   understand follow-up questions.
5. If document context is provided,
   prioritize information from it.
6. Never invent information from
   uploaded documents.
7. If the answer is not available in
   the document, clearly state that.
8. Format answers using Markdown.
9. Keep answers focused and avoid
   unnecessary repetition.

Conversation History:

{history_text}

Uploaded Document Context:

{document_context}

Current User Question:

{query}

Generate a helpful response.
"""

        return prompt

    # --------------------------------------------------
    # CHAT - NON-STREAMING
    # --------------------------------------------------

    def chat(
        self,
        query,
        history,
        document_chunks=None
    ):

        # Calculator tool
        if self._is_calculation(query):

            expression = self._extract_expression(
                query
            )

            if expression:

                try:

                    result = self.calculator.calculate(
                        expression
                    )

                    return (
                        f"The calculated result is "
                        f"{result}."
                    )

                except ValueError:
                    pass

        prompt = self._build_chat_prompt(
            query,
            history,
            document_chunks
        )

        return self.llm.generate_response(
            prompt
        )

    # --------------------------------------------------
    # CHAT - STREAMING
    # --------------------------------------------------

    def chat_stream(
        self,
        query,
        history,
        document_chunks=None
    ):

        # Calculator tool
        if self._is_calculation(query):

            expression = self._extract_expression(
                query
            )

            if expression:

                try:

                    result = self.calculator.calculate(
                        expression
                    )

                    yield (
                        f"The calculated result is "
                        f"{result}."
                    )

                    return

                except ValueError:
                    pass

        prompt = self._build_chat_prompt(
            query,
            history,
            document_chunks
        )

        yield from self.llm.generate_response_stream(
            prompt
        )

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    def summarize(self, text):

        # Limit input size to reduce latency.
        study_material = text[:6000]

        prompt = f"""
You are an academic study assistant.

Summarize the following study material.

Include:

1. Main concepts
2. Important definitions
3. Key points
4. A short conclusion

Use simple language.
Avoid unnecessary repetition.

Study Material:

{study_material}
"""

        return self.llm.generate_response(
            prompt
        )

    def summarize_stream(self, text):

        study_material = text[:6000]

        prompt = f"""
You are an academic study assistant.

Summarize the following study material.

Include:

1. Main concepts
2. Important definitions
3. Key points
4. A short conclusion

Use simple language.
Avoid unnecessary repetition.

Study Material:

{study_material}
"""

        yield from self.llm.generate_response_stream(
            prompt
        )

    # --------------------------------------------------
    # QUIZ GENERATOR
    # --------------------------------------------------

    def generate_quiz(self, text):

        study_material = text[:6000]

        prompt = f"""
You are an academic quiz generator.

Generate 5 multiple-choice questions
from the following study material.

Each question must contain:

- A question
- Four options
- The correct answer
- A short explanation

Use this format:

### Question 1

A. Option A
B. Option B
C. Option C
D. Option D

**Correct Answer:** B

**Explanation:** Explain why.

Study Material:

{study_material}
"""

        return self.llm.generate_response(
            prompt
        )

    # --------------------------------------------------
    # STUDY PLANNER
    # --------------------------------------------------

    def generate_study_plan(
        self,
        topics,
        days,
        hours_per_day
    ):

        prompt = f"""
You are an academic study planner.

Create a realistic study plan.

Topics:

{topics}

Available Days:

{days}

Study Hours Per Day:

{hours_per_day}

Include:

1. Daily topics
2. Revision sessions
3. Practice questions
4. A final revision day

Use a clear table format.
"""

        return self.llm.generate_response(
            prompt
        )
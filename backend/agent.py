import re

from backend.services.llm_service import LLMService
from backend.services.document_service import DocumentService
from backend.tools.calculator import Calculator


class StudyMateAgent:
    """Study assistant that uses uploaded material when relevant, not as a hard limit."""

    def __init__(self):
        self.llm = LLMService()
        self.document_service = DocumentService()
        self.calculator = Calculator()

    def _get_history_text(self, history):
        recent_history = history[-6:]
        formatted_history = []

        for message in recent_history:
            role = message.get("role", "user")
            content = str(message.get("content", ""))[:1200]
            formatted_history.append(f"{role.upper()}: {content}")

        return "\n".join(formatted_history)

    def _is_calculation(self, query):
        query = query.lower()

        keywords = [
            "calculate",
            "what is",
            "how much",
            "multiply",
            "divide",
            "addition",
            "subtract",
            "plus",
            "minus",
            "times",
        ]

        return any(keyword in query for keyword in keywords)

    def _extract_expression(self, query):
        query = query.replace(",", "")

        match = re.search(
            r"[-+]?\d+(?:\.\d+)?(?:\s*[\*+/\-^]\s*[-+]?\d+(?:\.\d+)?)+",
            query,
        )

        if not match:
            return None

        return match.group(0).replace("^", "**")

    def _build_chat_prompt(self, query, history, document_chunks=None):
        document_context = ""

        if document_chunks:
            try:
                document_context = self.document_service.search_documents(
                    query,
                    document_chunks,
                    top_k=3,
                )
            except Exception:
                document_context = ""

        history_text = self._get_history_text(history)

        return f"""
You are AI StudyMate, a friendly and capable academic study assistant.

Help the student understand concepts clearly and accurately. Use simple language,
examples, and Markdown formatting where useful. Follow the conversation history
to understand follow-up questions.

Uploaded document context is reference material:
- Use it when it is relevant to the user's question.
- Do not invent facts or claim that unsupported statements are present in the PDF.
- If the user's question is unrelated to the uploaded document, answer it using
  your general knowledge instead of refusing or saying you only know the document.
- When the document is relevant but incomplete, distinguish what the notes say
  from any additional general explanation.

Conversation history:
{history_text}

Relevant uploaded document excerpts:
{document_context or "(No relevant excerpt found.)"}

Current user question:
{query}

Give a useful, focused answer.
"""

    def chat(self, query, history, document_chunks=None):
        if self._is_calculation(query):
            expression = self._extract_expression(query)

            if expression:
                try:
                    result = self.calculator.calculate(expression)
                    return f"The calculated result is {result}."
                except (ValueError, TypeError, ZeroDivisionError):
                    pass

        prompt = self._build_chat_prompt(
            query,
            history,
            document_chunks,
        )

        return self.llm.generate_response(prompt)

    def chat_stream(self, query, history, document_chunks=None):
        if self._is_calculation(query):
            expression = self._extract_expression(query)

            if expression:
                try:
                    result = self.calculator.calculate(expression)
                    yield f"The calculated result is {result}."
                    return
                except (ValueError, TypeError, ZeroDivisionError):
                    pass

        prompt = self._build_chat_prompt(
            query,
            history,
            document_chunks,
        )

        yield from self.llm.generate_response_stream(prompt)

    def summarize(self, text):
        study_material = text[:10000]

        prompt = f"""You are an academic study assistant.
Summarize this study material in simple language. Include:
1. Main concepts
2. Important definitions
3. Key points
4. A short conclusion
Avoid unnecessary repetition.

Study Material:
{study_material}
"""

        return self.llm.generate_response(prompt)

    def summarize_stream(self, text):
        study_material = text[:10000]

        prompt = f"""You are an academic study assistant.
Summarize this study material in simple language. Include:
1. Main concepts
2. Important definitions
3. Key points
4. A short conclusion
Avoid unnecessary repetition.

Study Material:
{study_material}
"""

        yield from self.llm.generate_response_stream(prompt)

    def generate_quiz(self, text):
        study_material = text[:10000]

        prompt = f"""You are an academic quiz generator.
Generate 5 multiple-choice questions from this study material. Each must include
a question, four options, the correct answer, and a short explanation.
Use Markdown.

Study Material:
{study_material}
"""

        return self.llm.generate_response(prompt)

    def generate_study_plan(self, topics, days, hours_per_day):
        prompt = f"""You are an academic study planner. Create a realistic plan.

Topics:
{topics}

Available days: {days}
Study hours per day: {hours_per_day}

Include daily topics, revision sessions, practice questions, and a final revision day.
Use a clear Markdown table.
"""

        return self.llm.generate_response(prompt)
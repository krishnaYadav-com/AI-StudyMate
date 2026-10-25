import re

from io import BytesIO
from pypdf import PdfReader


class DocumentService:

    def extract_text(self, uploaded_file):

        pdf_reader = PdfReader(
            BytesIO(
                uploaded_file.getvalue()
            )
        )

        text = []

        for page in pdf_reader.pages:

            page_text = page.extract_text()

            if page_text:
                text.append(page_text)

        return "\n".join(text)

    def split_text(
        self,
        text,
        chunk_size=800,
        overlap=150
    ):

        words = text.split()

        chunks = []

        start = 0

        while start < len(words):

            end = start + chunk_size

            chunk = " ".join(
                words[start:end]
            )

            chunks.append(chunk)

            start += chunk_size - overlap

        return chunks

    def search_documents(
        self,
        query,
        chunks,
        top_k=2
    ):

        query_words = set(
            re.findall(
                r"\b\w+\b",
                query.lower()
            )
        )

        scored_chunks = []

        for chunk in chunks:

            chunk_words = set(
                re.findall(
                    r"\b\w+\b",
                    chunk.lower()
                )
            )

            score = len(
                query_words.intersection(
                    chunk_words
                )
            )

            scored_chunks.append(
                (score, chunk)
            )

        scored_chunks.sort(
            key=lambda item: item[0],
            reverse=True
        )

        relevant_chunks = [
            chunk
            for score, chunk in scored_chunks[:top_k]
            if score > 0
        ]

        # Keep document context small to reduce
        # the amount of text sent to the AI.
        context = "\n\n".join(
            relevant_chunks
        )

        return context[:3000]
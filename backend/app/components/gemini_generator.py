from google import genai

from backend.app.config import (
    GEMINI_API_KEY,
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


GENERATION_MODEL = (
    "gemini-3.6-flash"
)


def generate_answer(
    query: str,
    evidence,
    query_context: dict,
) -> str:

    if not evidence:

        return (
            "I could not find sufficient "
            "evidence in the uploaded "
            "academic documents."
        )

    evidence_text = []

    for index, document in enumerate(
        evidence,
        start=1,
    ):

        source = document.meta.get(
            "source",
            "Unknown",
        )

        page = document.meta.get(
            "page_number",
            "Unknown",
        )

        evidence_text.append(
            f"""
Evidence {index}
Source: {source}
Page: {page}

{document.content}
"""
        )

    combined_evidence = "\n".join(
        evidence_text
    )

    intent = query_context.get(
        "intent",
        "general",
    )

    learning_context = query_context.get(
        "learning_context",
        "conceptual_learning",
    )

    prompt = f"""
You are an academic assistant.

Answer the user's question using ONLY
the provided evidence.

Do not invent facts that are not supported
by the evidence.

If the evidence is insufficient, clearly
state that the available documents do not
contain enough information.

User question:
{query}

Educational intent:
{intent}

Learning context:
{learning_context}

Evidence:
{combined_evidence}

Instructions:

1. Give a clear academic answer.
2. Organize the answer according to the
   user's question.
3. If the question asks for multiple parts,
   cover each part separately.
4. Keep the explanation appropriate for
   academic learning.
5. Cite evidence using [Source, Page X].
"""

    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=prompt,
    )

    return response.text
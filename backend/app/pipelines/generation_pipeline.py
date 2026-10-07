from backend.app.components.gemini_generator import (
    generate_response,
)


def generate_rag_response(
    query: str,
    evidence: list,
    query_context: dict,
    personalization_context: dict | None = None,
) -> dict:
    """
    Generate a grounded academic response using
    Phase 5 evidence and Phase 7 learner preferences.
    """

    response = generate_response(
        query=query,
        evidence=evidence,
        query_context=query_context,
        personalization_context=personalization_context,
    )

    return {
        "query": query,

        "response": response,

        "evidence_count": len(evidence),

        "sources": [
            {
                "source": document.meta.get(
                    "source"
                ),

                "page": document.meta.get(
                    "page_number"
                ),

                "evidence_score": document.meta.get(
                    "evidence_score",
                    document.score,
                ),
            }

            for document in evidence
        ],

        "personalized": (
            personalization_context is not None
        ),
    }
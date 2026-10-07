from backend.app.components.query_analyser import analyze_query
from backend.app.components.retriever import retrieve_documents
from backend.app.components.evidence_composer import compose_evidence
from backend.app.components.evidence_validator import validate_evidence
from backend.app.components.evidence_reranker import rerank_evidence


def main():

    # ---------------------------------------------------------------
    # Test query
    # ---------------------------------------------------------------

    query = (
        "Explain the five building blocks that help "
        "maximise Customer Lifetime Value (CLV), "
        "including what each one is, why it matters, "
        "and how it contributes to CLV growth."
    )

    # ---------------------------------------------------------------
    # Phase 1 — Query Analysis
    # ---------------------------------------------------------------

    query_context = analyze_query(query)

    # ---------------------------------------------------------------
    # Phase 2 — Initial Retrieval
    # ---------------------------------------------------------------

    candidates = retrieve_documents(
        query=query,
        top_k=10,
    )

    # ---------------------------------------------------------------
    # Phase 2 — Evidence Composition
    # ---------------------------------------------------------------

    composed_evidence = compose_evidence(
        documents=candidates,
        query_context=query_context,
    )

    # ---------------------------------------------------------------
    # Phase 3 — Evidence Validation
    # ---------------------------------------------------------------

    validation = validate_evidence(
        query=query,
        documents=composed_evidence,
        query_context=query_context,
    )

    # ---------------------------------------------------------------
    # Pass Phase 3 discovered items to Phase 5
    # ---------------------------------------------------------------

    reranking_context = dict(query_context)

    reranking_context["discovered_items"] = (
        validation.get("discovered_items", [])
    )

    reranking_context["validation"] = validation

    # ---------------------------------------------------------------
    # Display Phase 1–3 results
    # ---------------------------------------------------------------

    print("\n" + "=" * 70)
    print("PHASE 5 — EVIDENCE RE-RANKING")
    print("=" * 70)

    print(
        f"Initial candidates: {len(candidates)}"
    )

    print(
        f"Composed evidence: {len(composed_evidence)}"
    )

    print(
        f"Validation sufficient: "
        f"{validation.get('sufficient', False)}"
    )

    print(
        f"Validation coverage: "
        f"{validation.get('coverage', 0):.3f}"
    )

    print(
        "Discovered items: "
        f"{validation.get('discovered_items', [])}"
    )

    print("\nPhase 4 items passed to Phase 5:")

    for item in validation.get(
        "discovered_items",
        [],
    ):
        print(f"  - {item}")

    # ---------------------------------------------------------------
    # Phase 5 — Evidence Re-ranking
    # ---------------------------------------------------------------

    reranked_evidence = rerank_evidence(
        query=query,
        documents=composed_evidence,
        query_context=reranking_context,
        top_k=7,
    )

    # ---------------------------------------------------------------
    # Quality report
    # ---------------------------------------------------------------

    evidence_scores = [
        document.meta.get(
            "evidence_score",
            0.0,
        )
        for document in reranked_evidence
    ]

    if evidence_scores:
        average_score = (
            sum(evidence_scores)
            / len(evidence_scores)
        )

        minimum_score = min(
            evidence_scores
        )

        maximum_score = max(
            evidence_scores
        )

    else:
        average_score = 0.0
        minimum_score = 0.0
        maximum_score = 0.0

    # ---------------------------------------------------------------
    # Display Phase 5 results
    # ---------------------------------------------------------------

    print("\n" + "=" * 70)
    print("PHASE 5 — RE-RANKED EVIDENCE")
    print("=" * 70)

    print(
        f"Final evidence count: "
        f"{len(reranked_evidence)}"
    )

    print(
        f"Average evidence score: "
        f"{average_score:.4f}"
    )

    print(
        f"Minimum evidence score: "
        f"{minimum_score:.4f}"
    )

    print(
        f"Maximum evidence score: "
        f"{maximum_score:.4f}"
    )

    # ---------------------------------------------------------------
    # Display each re-ranked evidence chunk
    # ---------------------------------------------------------------

    for index, document in enumerate(
        reranked_evidence,
        start=1,
    ):

        print("\n" + "-" * 70)
        print(f"EVIDENCE {index}")
        print("-" * 70)

        print(
            f"Source: "
            f"{document.meta.get('source', 'Unknown')}"
        )

        print(
            f"Page: "
            f"{document.meta.get('page_number', 'Unknown')}"
        )

        print(
            f"Chunk: "
            f"{document.meta.get('chunk_number', 'Unknown')}"
        )

        print(
            f"Original retrieval score: "
            f"{document.meta.get('retrieval_score', document.score)}"
        )

        print(
            f"Retrieval similarity: "
            f"{document.meta.get('retrieval_similarity', 0.0):.4f}"
        )

        print(
            f"Query relevance: "
            f"{document.meta.get('query_relevance', 0.0):.4f}"
        )

        print(
            f"Evidence item coverage: "
            f"{document.meta.get('evidence_coverage', 0.0):.4f}"
        )

        print(
            f"Content quality: "
            f"{document.meta.get('content_quality', 0.0):.4f}"
        )

        print(
            f"Structural quality: "
            f"{document.meta.get('structural_quality', 0.0):.4f}"
        )

        print(
            f"FINAL EVIDENCE SCORE: "
            f"{document.meta.get('evidence_score', 0.0):.4f}"
        )

        print("\nContent:")

        print(
            document.content.strip()
            if document.content
            else "[No content]"
        )


if __name__ == "__main__":
    main()
from backend.app.pipelines.adaptive_rag_pipeline import adaptive_retrieve


def main():
    query = (
        "Explain the five building blocks that help "
        "maximise Customer Lifetime Value (CLV), "
        "including what each one is, why it matters, "
        "and how it contributes to CLV growth."
    )

    result = adaptive_retrieve(
        query=query,
        initial_top_k=3,
        adaptive_top_k=8,
        max_iterations=3,
    )

    print("\n" + "=" * 70)
    print("PHASE 4 — ADAPTIVE RAG TRIGGERED")
    print("=" * 70)

    print(f"Adaptive status: {result['adaptive_status']}")
    print(f"Iterations: {result['iterations']}")
    print(
        f"Final sufficient: "
        f"{result['validation']['sufficient']}"
    )
    print(
        f"Final coverage: "
        f"{result['validation']['coverage']}"
    )
    print(
        f"Missing requirements: "
        f"{result['validation']['missing_requirements']}"
    )

    print("\n" + "=" * 70)
    print("DISCOVERED ITEMS")
    print("=" * 70)

    for item in result["validation"]["discovered_items"]:
        print(f"- {item}")

    print("\n" + "=" * 70)
    print("RETRIEVAL HISTORY")
    print("=" * 70)

    for history in result["retrieval_history"]:

        print(f"\nIteration: {history['iteration']}")
        print(f"Stage: {history['stage']}")
        print(f"Queries: {history['queries']}")

        if "candidate_count" in history:
            print(
                f"Candidate count: "
                f"{history['candidate_count']}"
            )

        if "new_candidate_count" in history:
            print(
                f"New candidate count: "
                f"{history['new_candidate_count']}"
            )

        print(
            f"Evidence count: "
            f"{history['evidence_count']}"
        )

        print(
            f"Sufficient: "
            f"{history['validation']['sufficient']}"
        )

        print(
            f"Coverage: "
            f"{history['validation']['coverage']}"
        )

        print(
            f"Missing requirements: "
            f"{history['validation']['missing_requirements']}"
        )

    print("\n" + "=" * 70)
    print("FINAL SELECTED EVIDENCE")
    print("=" * 70)

    for index, document in enumerate(
        result["evidence"],
        start=1,
    ):
        print("\n" + "-" * 70)
        print(f"EVIDENCE {index}")
        print("-" * 70)

        print(
            f"Source: "
            f"{document.meta.get('source')}"
        )

        print(
            f"Page: "
            f"{document.meta.get('page_number')}"
        )

        print(
            f"Chunk: "
            f"{document.meta.get('chunk_number')}"
        )

        print(
            f"Score: "
            f"{document.score}"
        )

        print()

        print(document.content)


if __name__ == "__main__":
    main()
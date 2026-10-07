from backend.app.pipelines.adaptive_rag_pipeline import adaptive_retrieve


def main():
    query = (
        "Explain the five building blocks that help "
        "maximise Customer Lifetime Value (CLV), and "
        "describe the role of each building block."
    )

    result = adaptive_retrieve(
        query=query,
        initial_top_k=5,
        adaptive_top_k=8,
        max_iterations=3,
    )

    print("\n" + "=" * 70)
    print("PHASE 4 — ADAPTIVE RAG NOT TRIGGERED")
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
        print(
            f"Evidence count: "
            f"{history['evidence_count']}"
        )
        print(
            f"Sufficient: "
            f"{history['validation']['sufficient']}"
        )


if __name__ == "__main__":
    main()
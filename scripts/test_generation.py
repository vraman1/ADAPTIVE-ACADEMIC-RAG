from backend.app.pipelines.adaptive_rag_pipeline import (
    adaptive_retrieve,
)

from backend.app.components.user_profile import (
    create_default_profile,
    record_interaction,
)


def main():

    query = (
        "Explain the five building blocks that help "
        "maximise Customer Lifetime Value (CLV), "
        "including what each one is, why it matters, "
        "and how it contributes to CLV growth."
    )

    # ===============================================================
    # CREATE LEARNER PROFILE
    # ===============================================================

    profile = create_default_profile()

    # ===============================================================
    # RUN COMPLETE ADAPTIVE RAG PIPELINE
    # ===============================================================

    result = adaptive_retrieve(
        query=query,
        initial_top_k=3,
        adaptive_top_k=8,
        max_iterations=3,
        user_profile=profile,
    )

    # ===============================================================
    # PHASE 7
    # ===============================================================

    personalization = result[
        "personalization"
    ]

    print("\n" + "=" * 70)
    print("PHASE 7 — LEARNER PERSONALIZATION")
    print("=" * 70)

    print(
        f"Preferred detail: "
        f"{personalization['preferred_detail']}"
    )

    print(
        f"Preferred format: "
        f"{personalization['preferred_format']}"
    )

    print(
        f"Preferred examples: "
        f"{personalization['preferred_examples']}"
    )

    print(
        f"Preferred citations: "
        f"{personalization['preferred_citations']}"
    )

    # ===============================================================
    # ADAPTIVE PIPELINE STATUS
    # ===============================================================

    print("\n" + "=" * 70)
    print("ADAPTIVE RAG PIPELINE")
    print("=" * 70)

    print(
        f"Adaptive status: "
        f"{result['adaptive_status']}"
    )

    print(
        f"Iterations: "
        f"{result['iterations']}"
    )

    print(
        f"Final evidence count: "
        f"{len(result['final_evidence'])}"
    )

    validation = result[
        "validation"
    ]

    print(
        f"Final validation sufficient: "
        f"{validation.get('sufficient')}"
    )

    print(
        f"Final validation coverage: "
        f"{validation.get('coverage')}"
    )

    # ===============================================================
    # QUERY CONTEXT
    # ===============================================================

    context = result[
        "query_context"
    ]

    print("\nQUERY CONTEXT")

    print(
        f"Intent: "
        f"{context.get('intent')}"
    )

    print(
        f"Learning context: "
        f"{context.get('learning_context')}"
    )

    print(
        f"Complexity: "
        f"{context.get('complexity')}"
    )

    print(
        f"Required count: "
        f"{context.get('required_count')}"
    )

    print(
        "Discovered items:"
    )

    for item in validation.get(
        "discovered_items",
        [],
    ):
        print(
            f"- {item}"
        )

    # ===============================================================
    # PHASE 5
    # ===============================================================

    print("\n" + "=" * 70)
    print("PHASE 5 EVIDENCE USED FOR GENERATION")
    print("=" * 70)

    for index, document in enumerate(
        result["final_evidence"],
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

        score = document.meta.get(
            "evidence_score",
            document.score,
        )

        print(
            f"{index}. "
            f"{source} | "
            f"Page {page} | "
            f"Evidence score: {score:.4f}"
        )

    # ===============================================================
    # PHASE 6
    # ===============================================================

    generation = result[
        "generation"
    ]

    print("\n" + "=" * 70)
    print("PHASE 6 — PERSONALIZED RAG GENERATION")
    print("=" * 70)

    print(
        f"Personalized: "
        f"{generation.get('personalized')}"
    )

    print("\nFINAL ACADEMIC RESPONSE\n")

    print(
        generation["response"]
    )

    # ===============================================================
    # UPDATE PROFILE
    # ===============================================================

    profile = record_interaction(
        profile=profile,
        query=query,
        query_context=context,
        response=generation[
            "response"
        ],
    )

    print("\n" + "=" * 70)
    print("PROFILE UPDATED")
    print("=" * 70)

    print(
        f"Interactions recorded: "
        f"{profile['interaction_count']}"
    )


if __name__ == "__main__":
    main()
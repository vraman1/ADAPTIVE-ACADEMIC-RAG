from pathlib import Path
import sys


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]


if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from backend.app.pipelines.adaptive_rag_pipeline import (
    adaptive_retrieve,
)


def print_result(
    result,
):

    print("\n")
    print("=" * 80)
    print("ADAPTIVE RAG TEST")
    print("=" * 80)

    print(
        f"\nQuery:\n"
        f"{result['query']}"
    )

    print("\nQuery Context:")

    for key, value in result[
        "query_context"
    ].items():

        print(
            f"  {key}: {value}"
        )

    print("\nFinal Validation:")

    validation = result[
        "validation"
    ]

    for key, value in validation.items():

        print(
            f"  {key}: {value}"
        )

    print(
        "\nAdaptive Retrieval:",
        result[
            "adaptive_retrieval"
        ],
    )

    print(
        "Iterations:",
        result[
            "iterations"
        ],
    )

    print("\nRetrieval History:")

    for history in result[
        "retrieval_history"
    ]:

        print(
            f"\n  Iteration: "
            f"{history['iteration']}"
        )

        print(
            f"  Stage: "
            f"{history['stage']}"
        )

        print(
            f"  Candidate count: "
            f"{history.get('candidate_count', history.get('total_candidate_count'))}"
        )

        print(
            f"  Evidence count: "
            f"{history['evidence_count']}"
        )

        print(
            f"  Validation: "
            f"{history['validation']}"
        )

        if history.get("queries"):

            print("  Queries:")

            for query in history[
                "queries"
            ]:

                print(
                    f"    - {query}"
                )

    print(
        "\nSelected Evidence:"
    )

    for index, document in enumerate(
        result["evidence"],
        start=1,
    ):

        print(
            "\n"
            + "-" * 80
        )

        print(
            f"Evidence {index}"
        )

        print(
            f"Score: "
            f"{document.score}"
        )

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
            "\nContent:"
        )

        print(
            document.content
        )


def main():

    query = (
        "Explain the five tiers "
        "of Streaming Analytics Architecture."
    )

    result = adaptive_retrieve(
        query=query,

        # Small initial retrieval deliberately
        # makes adaptive behavior easy to demonstrate.
        initial_top_k=2,

        # Controlled adaptive retrieval.
        adaptive_top_k=8,

        max_iterations=3,
    )

    print_result(
        result
    )


if __name__ == "__main__":

    main()
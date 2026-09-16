from pathlib import Path

from backend.app.pipelines.adaptive_rag_pipeline import adaptive_retrieve
from backend.app.components.gemini_generator import generate_answer


# --------------------------------------------------
# PROJECT DATA DIRECTORY
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data" / "raw_documents"


# --------------------------------------------------
# FILE DISCOVERY
# --------------------------------------------------

def get_pdf_files():
    """
    Automatically discover all PDF files inside
    data/raw_documents.

    No PDF filename is hardcoded.
    """

    if not DATA_DIR.exists():
        return []

    return sorted(
        [
            file
            for file in DATA_DIR.iterdir()
            if file.is_file()
            and file.suffix.lower() == ".pdf"
        ],
        key=lambda file: file.name.lower(),
    )


# --------------------------------------------------
# FILE SELECTION
# --------------------------------------------------

def select_pdf():
    """
    Display available PDFs and allow the user
    to select exactly one.
    """

    pdf_files = get_pdf_files()

    if not pdf_files:
        print("\nNo PDF files found.")

        print("\nExpected directory:")
        print(DATA_DIR)

        return None

    print("\n" + "=" * 70)
    print("                  AVAILABLE ACADEMIC FILES")
    print("=" * 70)

    for index, pdf_file in enumerate(pdf_files, start=1):
        print(f"\n{index}. {pdf_file.name}")

    print("\n" + "-" * 70)

    while True:

        choice = input(
            "\nSelect a PDF number "
            "(or type 'exit' to quit): "
        ).strip()

        if choice.lower() in {"exit", "quit"}:
            return None

        if not choice.isdigit():
            print("Please enter a valid number.")

            continue

        selected_index = int(choice)

        if 1 <= selected_index <= len(pdf_files):

            selected_file = pdf_files[selected_index - 1]

            print("\nSelected PDF:")
            print(f"→ {selected_file.name}")

            return selected_file.name

        print(
            f"Please enter a number between "
            f"1 and {len(pdf_files)}."
        )


# --------------------------------------------------
# TITLE FORMATTER
# --------------------------------------------------

def format_title(text: str) -> str:
    return text.replace("_", " ").title()


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():

    print("=" * 70)
    print("                 ADAPTIVE ACADEMIC RAG")
    print("=" * 70)

    # --------------------------------------------------
    # SELECT PDF
    # --------------------------------------------------

    selected_source = select_pdf()

    if selected_source is None:

        print("\nExiting...")
        return

    # --------------------------------------------------
    # QUESTION LOOP
    # --------------------------------------------------

    while True:

        query = input(
            "\nEnter your question "
            "(or type 'exit' to quit): "
        ).strip()

        if query.lower() in {"exit", "quit"}:

            print("\nExiting...")
            break

        if not query:

            print("Please enter a question.")
            continue

        # --------------------------------------------------
        # ADAPTIVE RAG
        # --------------------------------------------------

        print(
            "\nAnalyzing query and retrieving "
            "academic evidence..."
        )

        result = adaptive_retrieve(
            query=query,
            source=selected_source,
            initial_top_k=2,
            adaptive_top_k=8,
            max_iterations=3,
        )

        # --------------------------------------------------
        # GENERATE ANSWER
        # --------------------------------------------------

        answer = generate_answer(
            query=query,
            evidence=result["evidence"],
            query_context=result["query_context"],
        )

        query_context = result["query_context"]
        validation = result["validation"]

        # --------------------------------------------------
        # ANSWER
        # --------------------------------------------------

        print("\n" + "=" * 70)
        print("                         ANSWER")
        print("=" * 70)

        print()
        print(answer)

        # --------------------------------------------------
        # SELECTED SOURCE
        # --------------------------------------------------

        print("\n" + "=" * 70)
        print("                    SELECTED SOURCE")
        print("=" * 70)

        print(f"\nPDF: {result['selected_source']}")

        # --------------------------------------------------
        # ADAPTIVE RAG STATUS
        # --------------------------------------------------

        print("\n" + "=" * 70)
        print("                    ADAPTIVE RAG STATUS")
        print("=" * 70)

        print(
            f"\nAdaptive Retrieval: "
            f"{result['adaptive_status']}"
        )

        if result["adaptive_status"] == "Triggered":

            print(
                "Reason: Initial evidence was insufficient"
            )

            print(
                f"Retrieval Iterations: "
                f"{result['iterations']}"
            )

            print(
                "Initial Evidence: Insufficient"
            )

            print(
                "Adaptive Re-retrieval: Completed"
            )

            print(
                "Evidence Re-validation: Completed"
            )

        else:

            print(
                "Reason: Initial evidence was sufficient"
            )

            print(
                f"Retrieval Iterations: "
                f"{result['iterations']}"
            )

            print(
                "Initial Evidence: Sufficient"
            )

            print(
                "Adaptive Re-retrieval: Not required"
            )

        # --------------------------------------------------
        # QUERY UNDERSTANDING
        # --------------------------------------------------

        print("\n" + "=" * 70)
        print("                  QUERY UNDERSTANDING")
        print("=" * 70)

        print(
            f"\nIntent: "
            f"{format_title(query_context['intent'])}"
        )

        print(
            f"Learning Context: "
            f"{format_title(query_context['learning_context'])}"
        )

        print(
            f"Complexity: "
            f"{format_title(query_context['complexity'])}"
        )

        print(
            f"Multi-Concept: "
            f"{'Yes' if query_context['multi_concept'] else 'No'}"
        )

        required_count = query_context.get(
            "required_count"
        )

        if required_count is not None:

            print(
                f"Required Count: "
                f"{required_count}"
            )

        else:

            print(
                "Required Count: Not specified"
            )

        # --------------------------------------------------
        # EVIDENCE VALIDATION
        # --------------------------------------------------

        print("\n" + "=" * 70)
        print("                  EVIDENCE VALIDATION")
        print("=" * 70)

        print(
            f"\nEvidence Sufficient: "
            f"{'Yes' if validation['sufficient'] else 'No'}"
        )

        print(
            f"Coverage Score: "
            f"{validation['coverage_score']:.2f}"
        )

        print(
            f"Average Retrieval Score: "
            f"{validation['average_score']:.2f}"
        )

        missing_parts = validation.get(
            "missing_parts",
            []
        )

        if missing_parts:

            print(
                f"Missing Evidence: "
                f"{missing_parts}"
            )

        else:

            print(
                "Missing Evidence: None"
            )

        print(
            f"Validation Reason: "
            f"{validation['reason']}"
        )

        # --------------------------------------------------
        # TOP EVIDENCE
        # --------------------------------------------------

        print("\n" + "=" * 70)
        print("                       TOP EVIDENCE")
        print("=" * 70)

        if result["evidence"]:

            top_document = result["evidence"][0]

            source = top_document.meta.get(
                "source",
                "Unknown"
            )

            page = top_document.meta.get(
                "page_number",
                "Unknown"
            )

            score = top_document.score

            print(f"\nSource: {source}")
            print(f"Page: {page}")

            if score is not None:

                print(
                    f"Retrieval Score: "
                    f"{score:.2f}"
                )

            else:

                print(
                    "Retrieval Score: N/A"
                )

            print("\nContent:")
            print("-" * 70)

            print(top_document.content)

            print("-" * 70)

        else:

            print("\nNo evidence retrieved.")

        # --------------------------------------------------
        # RETRIEVAL PROCESS
        # --------------------------------------------------

        print("\n" + "=" * 70)
        print("                  RETRIEVAL PROCESS")
        print("=" * 70)

        for history in result[
            "retrieval_history"
        ]:

            iteration = history[
                "iteration"
            ]

            stage = history[
                "stage"
            ]

            print(
                f"\nIteration {iteration}: "
                f"{format_title(stage)}"
            )

            print(
                f"Evidence Count: "
                f"{history['evidence_count']}"
            )

            if "candidate_count" in history:

                print(
                    f"Candidate Count: "
                    f"{history['candidate_count']}"
                )

            if "new_candidate_count" in history:

                print(
                    f"New Candidates: "
                    f"{history['new_candidate_count']}"
                )

            if "total_candidate_count" in history:

                print(
                    f"Total Candidates: "
                    f"{history['total_candidate_count']}"
                )

            print("Queries Used:")

            for retrieval_query in history[
                "queries"
            ]:

                print(
                    f"  → {retrieval_query}"
                )

            history_validation = history[
                "validation"
            ]

            status = (
                "Sufficient"
                if history_validation["sufficient"]
                else "Insufficient"
            )

            print(
                f"Validation: {status}"
            )

            print(
                f"Coverage: "
                f"{history_validation['coverage_score']:.2f}"
            )

            print(
                f"Average Score: "
                f"{history_validation['average_score']:.2f}"
            )

        print("\n" + "=" * 70)


# --------------------------------------------------
# PROGRAM ENTRY
# --------------------------------------------------

if __name__ == "__main__":
    main()
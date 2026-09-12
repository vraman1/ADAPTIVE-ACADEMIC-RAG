from pathlib import Path
import sys


# Project root
PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]


if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from backend.app.pipelines.indexing_pipeline import (
    ingest_pdf,
)


DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw_documents"
)


def main():

    pdf_files = list(
        DATA_DIR.glob("*.pdf")
    )

    if not pdf_files:

        print(
            f"No PDF files found in: {DATA_DIR}"
        )

        return

    total = 0

    for pdf_file in pdf_files:

        print(
            f"\nIndexing: {pdf_file.name}"
        )

        count = ingest_pdf(
            str(pdf_file)
        )

        print(
            f"Chunks created: {count}"
        )

        total += count

    print(
        f"\nTotal chunks indexed: {total}"
    )


if __name__ == "__main__":

    main()
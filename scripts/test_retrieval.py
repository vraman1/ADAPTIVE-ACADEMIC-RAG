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


from backend.app.components.retriever import (
    retrieve_documents,
)


query = (
    "Explain the five tiers "
    "of Streaming Analytics Architecture."
)


documents = retrieve_documents(
    query=query,
    top_k=10,
)


print(
    f"\nQuery: {query}\n"
)

print(
    f"Retrieved documents: "
    f"{len(documents)}\n"
)


for index, document in enumerate(
    documents,
    start=1,
):

    print("=" * 80)

    print(
        f"Result {index}"
    )

    print(
        f"Score: {document.score}"
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

print("=" * 80)
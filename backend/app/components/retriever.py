from haystack import Document
from haystack_integrations.components.retrievers.pgvector import (
    PgvectorEmbeddingRetriever,
)

from backend.app.components.embedding_service import embed_query
from backend.app.haystack_store import document_store


retriever = PgvectorEmbeddingRetriever(
    document_store=document_store
)


def retrieve_documents(
    query: str,
    top_k: int = 5,
    source: str | None = None,
) -> list[Document]:

    if not query or not query.strip():
        return []

    query_embedding = embed_query(query)

    filters = None

    if source:
        filters = {
            "field": "meta.source",
            "operator": "==",
            "value": source,
        }

    result = retriever.run(
        query_embedding=query_embedding,
        top_k=top_k,
        filters=filters,
    )

    return result.get("documents", [])
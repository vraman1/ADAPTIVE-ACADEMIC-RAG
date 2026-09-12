from haystack import Document

from haystack_integrations.components.retrievers.pgvector import (
    PgvectorEmbeddingRetriever,
)

from backend.app.components.embedding_service import (
    embed_query,
)

from backend.app.haystack_store import (
    document_store,
)


retriever = PgvectorEmbeddingRetriever(
    document_store=document_store
)


def retrieve_documents(
    query: str,
    top_k: int = 5,
) -> list[Document]:

    if not query or not query.strip():
        return []

    query_embedding = embed_query(
        query
    )

    result = retriever.run(
        query_embedding=query_embedding,
        top_k=top_k,
    )

    return result.get(
        "documents",
        []
    )
from backend.app.config import PG_CONN_STR
from haystack_integrations.document_stores.pgvector import PgvectorDocumentStore

# Gemini embedding dimension selected for this project.
EMBEDDING_DIMENSION = 768

document_store = PgvectorDocumentStore(
    table_name="academic_documents",
    embedding_dimension=EMBEDDING_DIMENSION,
    vector_function="cosine_similarity",
    search_strategy="hnsw",
    create_extension=False,
    recreate_table=False,
)
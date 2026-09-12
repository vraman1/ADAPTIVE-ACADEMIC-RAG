from google import genai
from google.genai import types

from backend.app.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)

EMBEDDING_MODEL = "gemini-embedding-001"

EMBEDDING_DIMENSION = 768


def embed_documents(
    texts: list[str],
) -> list[list[float]]:

    if not texts:
        return []

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            output_dimensionality=EMBEDDING_DIMENSION,
        ),
    )

    return [
        embedding.values
        for embedding in response.embeddings
    ]


def embed_query(
    query: str,
) -> list[float]:

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query.strip(),
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=EMBEDDING_DIMENSION,
        ),
    )

    return response.embeddings[0].values
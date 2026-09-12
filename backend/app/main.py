from fastapi import FastAPI
from pydantic import BaseModel

from backend.app.pipelines.adaptive_rag_pipeline import (
    adaptive_retrieve,
)

from backend.app.components.gemini_generator import (
    generate_answer,
)


app = FastAPI(
    title="Adaptive Academic RAG",
    version="1.0.0",
)


class QueryRequest(
    BaseModel
):

    query: str


@app.get("/")
def root():

    return {
        "message": "Adaptive Academic RAG API is running."
    }


@app.post("/query")
def query_rag(
    request: QueryRequest,
):

    result = adaptive_retrieve(
        request.query
    )

    answer = generate_answer(
        query=request.query,
        evidence=result["evidence"],
        query_context=result[
            "query_context"
        ],
    )

    return {
        "query": request.query,

        "answer": answer,

        "query_context":
            result[
                "query_context"
            ],

        "adaptive_retrieval":
            result[
                "adaptive_retrieval"
            ],

        "iterations":
            result[
                "iterations"
            ],

        "validation":
            result[
                "validation"
            ],

        "retrieval_history":
            result[
                "retrieval_history"
            ],
    }
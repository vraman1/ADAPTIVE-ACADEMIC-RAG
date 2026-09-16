from backend.app.components.query_analyser import analyze_query
from backend.app.components.retriever import retrieve_documents
from backend.app.components.evidence_composer import compose_evidence
from backend.app.components.evidence_validator import validate_evidence


def document_key(document):
    return (
        document.meta.get("source"),
        document.meta.get("page_number"),
        document.meta.get("chunk_number"),
    )


def build_adaptive_queries(query, context, validation):
    missing_parts = validation.get("missing_parts", [])

    if missing_parts:
        queries = []

        for part in missing_parts:
            queries.extend([
                f"{query} part {part}",
                f"{query} section {part}",
                f"{query} {part}",
            ])

        return queries

    intent = context.get("intent", "general")

    adaptive_queries = {
        "definition": [
            f"{query} definition",
            f"{query} meaning",
            f"{query} concept",
        ],

        "comparison": [
            f"{query} comparison",
            f"{query} differences",
            f"{query} similarities",
        ],

        "explanation": [
            f"{query} detailed explanation",
            f"{query} key concepts",
            f"{query} important points",
        ],

        "summarization": [
            f"{query} key points",
            f"{query} summary",
            f"{query} important information",
        ],

        "example": [
            f"{query} examples",
            f"{query} applications",
            f"{query} use cases",
        ],

        "general": [
            f"{query} key concepts",
            f"{query} important points",
            f"{query} details",
        ],
    }

    return adaptive_queries.get(
        intent,
        adaptive_queries["general"],
    )


def merge_candidates(
    existing_documents,
    new_documents,
    max_candidates=40,
):
    all_documents = existing_documents + new_documents

    all_documents = sorted(
        all_documents,
        key=lambda document: (
            document.score
            if document.score is not None
            else 0
        ),
        reverse=True,
    )

    merged = []
    seen = set()

    for document in all_documents:
        key = document_key(document)

        if key in seen:
            continue

        seen.add(key)
        merged.append(document)

        if len(merged) >= max_candidates:
            break

    return merged


def adaptive_retrieve(
    query,
    source=None,
    initial_top_k=5,
    adaptive_top_k=8,
    max_iterations=3,
):
    """
    Adaptive RAG retrieval pipeline.

    If source is provided, retrieval is restricted
    to that specific academic document.
    """

    query_context = analyze_query(query)

    # --------------------------------------------------
    # ITERATION 1: INITIAL RETRIEVAL
    # --------------------------------------------------

    candidates = retrieve_documents(
        query=query,
        top_k=initial_top_k,
        source=source,
    )

    evidence = compose_evidence(
        documents=candidates,
        query_context=query_context,
    )

    validation = validate_evidence(
        query=query,
        documents=evidence,
        query_context=query_context,
    )

    retrieval_history = [
        {
            "iteration": 1,
            "stage": "initial_retrieval",
            "queries": [query],
            "candidate_count": len(candidates),
            "evidence_count": len(evidence),
            "validation": validation,
        }
    ]

    iteration = 1

    # --------------------------------------------------
    # ADAPTIVE RE-RETRIEVAL
    # --------------------------------------------------

    while (
        not validation.get("sufficient", False)
        and iteration < max_iterations
    ):

        targeted_queries = build_adaptive_queries(
            query=query,
            context=query_context,
            validation=validation,
        )

        new_candidates = []

        for targeted_query in targeted_queries:

            results = retrieve_documents(
                query=targeted_query,
                top_k=adaptive_top_k,
                source=source,
            )

            new_candidates.extend(results)

        candidates = merge_candidates(
            existing_documents=candidates,
            new_documents=new_candidates,
            max_candidates=40,
        )

        evidence = compose_evidence(
            documents=candidates,
            query_context=query_context,
        )

        validation = validate_evidence(
            query=query,
            documents=evidence,
            query_context=query_context,
        )

        iteration += 1

        retrieval_history.append(
            {
                "iteration": iteration,
                "stage": "adaptive_retrieval",
                "queries": targeted_queries,
                "new_candidate_count": len(new_candidates),
                "total_candidate_count": len(candidates),
                "evidence_count": len(evidence),
                "validation": validation,
            }
        )

    adaptive_status = (
        "Triggered"
        if iteration > 1
        else "Not Required"
    )

    return {
        "query": query,

        # Selected PDF
        "selected_source": source,

        # Query understanding
        "query_context": query_context,

        # Retrieval
        "candidates": candidates,
        "evidence": evidence,

        # Validation
        "validation": validation,

        # Adaptive information
        "iterations": iteration,
        "adaptive_status": adaptive_status,
        "adaptive_retrieval": iteration > 1,

        # Full history
        "retrieval_history": retrieval_history,
    }
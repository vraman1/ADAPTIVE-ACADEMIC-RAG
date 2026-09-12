from backend.app.components.query_analyser import (
    analyze_query,
)

from backend.app.components.retriever import (
    retrieve_documents,
)

from backend.app.components.evidence_composer import (
    compose_evidence,
)

from backend.app.components.evidence_validator import (
    validate_evidence,
    filter_relevant_documents,
)


def build_targeted_queries(
    query,
    context,
    validation,
):

    missing_parts = validation.get(
        "missing_parts",
        [],
    )

    if missing_parts:

        queries = []

        for part in missing_parts:

            queries.extend(
                [
                    f"{query} part {part}",
                    f"{query} section {part}",
                    f"{query} {part}",
                ]
            )

        return queries

    intent = context.get(
        "intent",
        "general",
    )

    targeted = {

        "definition": [
            f"{query} definition",
            f"{query} concept",
        ],

        "comparison": [
            f"{query} comparison",
            f"{query} differences",
        ],

        "explanation": [
            f"{query} detailed explanation",
            f"{query} key components",
        ],

        "summarization": [
            f"{query} key points",
            f"{query} summary",
        ],

        "example": [
            f"{query} examples",
            f"{query} applications",
        ],

        "general": [
            f"{query} key concepts",
            f"{query} important points",
        ],
    }

    return targeted.get(
        intent,
        targeted["general"],
    )


def document_key(
    document,
):

    return (
        document.meta.get("source"),
        document.meta.get("page_number"),
        document.meta.get("chunk_number"),
    )


def merge_candidates(
    existing_documents,
    new_documents,
    max_candidates=40,
):

    merged = []

    seen = set()

    all_documents = sorted(
        existing_documents
        + new_documents,

        key=lambda document: (
            document.score
            if document.score is not None
            else 0
        ),

        reverse=True,
    )

    for document in all_documents:

        key = document_key(
            document
        )

        if key in seen:
            continue

        seen.add(key)

        merged.append(
            document
        )

        if len(merged) >= max_candidates:
            break

    return merged


def prioritize_missing_evidence(
    documents,
    validation,
):

    missing_parts = validation.get(
        "missing_parts",
        [],
    )

    if not missing_parts:
        return documents

    priority = []

    normal = []

    for document in documents:

        text = document.content.lower()

        found = False

        for part in missing_parts:

            patterns = [
                f"tier {part}",
                f"tier {part}:",
                f"part {part}",
                f"section {part}",
                f"stage {part}",
                f"step {part}",
            ]

            if any(
                pattern in text
                for pattern in patterns
            ):

                found = True

                break

        if found:

            priority.append(
                document
            )

        else:

            normal.append(
                document
            )

    return priority + normal


def adaptive_retrieve(
    query,
    initial_top_k=8,
    adaptive_top_k=8,
    max_iterations=3,
):

    # --------------------------------------------------
    # STEP 1: Query analysis
    # --------------------------------------------------

    query_context = analyze_query(
        query
    )

    # --------------------------------------------------
    # STEP 2: Initial retrieval
    # --------------------------------------------------

    candidates = retrieve_documents(
        query=query,
        top_k=initial_top_k,
    )

    # --------------------------------------------------
    # STEP 3: Evidence composition
    # --------------------------------------------------

    evidence = compose_evidence(
        documents=candidates,
        query_context=query_context,
    )

    # --------------------------------------------------
    # STEP 4: Evidence validation
    # --------------------------------------------------

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
            "candidate_count": len(
                candidates
            ),
            "evidence_count": len(
                evidence
            ),
            "validation": validation,
        }
    ]

    iteration = 1

    # --------------------------------------------------
    # STEP 5: Adaptive loop
    # --------------------------------------------------

    while (
        not validation.get(
            "sufficient",
            False,
        )
        and iteration < max_iterations
    ):

        targeted_queries = (
            build_targeted_queries(
                query=query,
                context=query_context,
                validation=validation,
            )
        )

        new_candidates = []

        # Targeted retrieval
        for targeted_query in targeted_queries:

            results = retrieve_documents(
                query=targeted_query,
                top_k=adaptive_top_k,
            )

            new_candidates.extend(
                results
            )

        # --------------------------------------------------
        # Merge and rank
        # --------------------------------------------------

        candidates = merge_candidates(
            candidates,
            new_candidates,
            max_candidates=40,
        )

        # --------------------------------------------------
        # Prioritize missing evidence
        # --------------------------------------------------

        candidates = (
            prioritize_missing_evidence(
                candidates,
                validation,
            )
        )

        # --------------------------------------------------
        # Re-compose evidence
        # --------------------------------------------------

        evidence = compose_evidence(
            documents=candidates,
            query_context=query_context,
        )

        # Remove weak/unrelated evidence
        evidence = filter_relevant_documents(
            evidence
        )

        # --------------------------------------------------
        # Re-validate
        # --------------------------------------------------

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
                "new_candidate_count": len(
                    new_candidates
                ),
                "total_candidate_count": len(
                    candidates
                ),
                "evidence_count": len(
                    evidence
                ),
                "validation": validation,
            }
        )

    # --------------------------------------------------
    # STEP 6: Return adaptive RAG state
    # --------------------------------------------------

    return {
        "query": query,
        "query_context": query_context,
        "candidates": candidates,
        "evidence": evidence,
        "validation": validation,
        "iterations": iteration,
        "adaptive_retrieval": (
            iteration > 1
        ),
        "retrieval_history": retrieval_history,
    }
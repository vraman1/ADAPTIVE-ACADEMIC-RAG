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
)

from backend.app.components.evidence_reranker import (
    rerank_evidence,
)

from backend.app.components.user_profile import (
    ensure_profile,
    build_personalization_context,
)

from backend.app.pipelines.generation_pipeline import (
    generate_rag_response,
)


# ==================================================================
# DOCUMENT KEY
# ==================================================================

def document_key(document):
    """
    Create a unique identifier for a retrieved document chunk.
    """

    return (
        document.meta.get("source"),
        document.meta.get("page_number"),
        document.meta.get("chunk_number"),
    )


# ==================================================================
# TARGETED QUERY BUILDER
# ==================================================================

def build_targeted_queries(
    query,
    context,
    validation,
):
    """
    Build additional retrieval queries when the current
    evidence is not sufficient.
    """

    missing_parts = validation.get(
        "missing_parts",
        [],
    )

    missing_requirements = validation.get(
        "missing_requirements",
        [],
    )

    queries = []

    # --------------------------------------------------------------
    # Priority 1: Missing parts
    # --------------------------------------------------------------

    if missing_parts:

        for part in missing_parts:

            queries.append(
                f"{query} part {part}"
            )

            queries.append(
                f"{query} section {part}"
            )

        return list(
            dict.fromkeys(queries)
        )

    # --------------------------------------------------------------
    # Priority 2: Missing requirements
    # --------------------------------------------------------------

    for requirement in missing_requirements:

        requirement_lower = (
            str(requirement).lower()
        )

        if "requested items" in requirement_lower:

            queries.extend(
                [
                    f"{query} building blocks",
                    f"{query} components",
                    f"{query} key areas",
                    f"{query} main elements",
                    f"{query} framework",
                ]
            )

        else:

            queries.extend(
                [
                    f"{query} {requirement}",
                    f"{requirement} {query}",
                ]
            )

    # --------------------------------------------------------------
    # Priority 3: Intent-based fallback
    # --------------------------------------------------------------

    if not queries:

        intent = context.get(
            "intent",
            "general",
        )

        if intent == "comparison":

            queries.extend(
                [
                    f"{query} comparison",
                    f"{query} differences",
                ]
            )

        elif intent == "definition":

            queries.extend(
                [
                    f"{query} definition",
                    f"{query} meaning",
                ]
            )

        elif intent == "example":

            queries.extend(
                [
                    f"{query} examples",
                    f"{query} applications",
                ]
            )

        elif intent == "summarization":

            queries.extend(
                [
                    f"{query} summary",
                    f"{query} key points",
                ]
            )

        elif intent == "explanation":

            queries.extend(
                [
                    f"{query} detailed explanation",
                    f"{query} key concepts",
                ]
            )

        else:

            queries.extend(
                [
                    f"{query} key concepts",
                    f"{query} important information",
                ]
            )

    # --------------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------------

    unique_queries = []
    seen = set()

    for retrieval_query in queries:

        normalized = (
            retrieval_query
            .lower()
            .strip()
        )

        if not normalized:
            continue

        if normalized in seen:
            continue

        seen.add(normalized)

        unique_queries.append(
            retrieval_query
        )

    return unique_queries


# ==================================================================
# MERGE CANDIDATES
# ==================================================================

def merge_candidates(
    existing_documents,
    new_documents,
    max_candidates=40,
):
    """
    Merge existing and newly retrieved documents,
    remove duplicates, and retain the strongest
    retrieval candidates.
    """

    all_documents = (
        existing_documents
        + new_documents
    )

    # Highest retrieval score first.

    all_documents = sorted(
        all_documents,
        key=lambda document: (
            document.score
            if document.score is not None
            else 0.0
        ),
        reverse=True,
    )

    merged = []
    seen = set()

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


# ==================================================================
# ADAPTIVE RETRIEVAL PIPELINE
# ==================================================================

def adaptive_retrieve(
    query,
    source=None,
    initial_top_k=5,
    adaptive_top_k=8,
    max_iterations=3,
    user_profile=None,
):
    """
    Main Adaptive Academic RAG pipeline.

    Pipeline:

        Query
          ↓
        Phase 1: Query Analysis
          ↓
        Initial Retrieval
          ↓
        Phase 2: Evidence Composition
          ↓
        Phase 3: Evidence Validation
          ↓
        Phase 4: Targeted Re-retrieval if insufficient
          ↓
        Re-composition
          ↓
        Re-validation
          ↓
        Phase 5: Evidence Re-ranking
          ↓
        Phase 7: Learner Personalization
          ↓
        Phase 6: RAG Generation
          ↓
        Final Academic Response
    """

    # ==============================================================
    # INPUT VALIDATION
    # ==============================================================

    if not query or not query.strip():

        return {
            "query": query,
            "selected_source": source,
            "query_context": {},
            "candidates": [],
            "composed_evidence": [],
            "evidence": [],
            "final_evidence": [],
            "validation": {
                "sufficient": False,
                "coverage": 0.0,
                "missing_requirements": [],
                "missing_parts": [],
                "discovered_items": [],
            },
            "iterations": 0,
            "adaptive_status": "Not Required",
            "adaptive_retrieval": False,
            "retrieval_history": [],
            "personalization": None,
            "generation": None,
        }

    # ==============================================================
    # PHASE 1
    # QUERY & EDUCATIONAL CONTEXT ANALYSIS
    # ==============================================================

    query_context = analyze_query(
        query
    )

    # ==============================================================
    # PHASE 7
    # LEARNER PROFILE
    # ==============================================================

    profile = ensure_profile(
        user_profile
    )

    personalization_context = (
        build_personalization_context(
            profile
        )
    )

    # ==============================================================
    # INITIAL RETRIEVAL
    # ==============================================================

    candidates = retrieve_documents(
        query=query,
        top_k=initial_top_k,
        source=source,
    )

    initial_candidates = list(
        candidates
    )

    # ==============================================================
    # PHASE 2
    # INITIAL EVIDENCE COMPOSITION
    # ==============================================================

    evidence = compose_evidence(
        documents=candidates,
        query_context=query_context,
    )

    # ==============================================================
    # PHASE 3
    # INITIAL EVIDENCE VALIDATION
    # ==============================================================

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

    # ==============================================================
    # PHASE 4
    # ADAPTIVE RE-RETRIEVAL
    # ==============================================================

    while (
        not validation.get(
            "sufficient",
            False,
        )
        and iteration < max_iterations
    ):

        # ----------------------------------------------------------
        # Determine missing evidence
        # ----------------------------------------------------------

        targeted_queries = (
            build_targeted_queries(
                query=query,
                context=query_context,
                validation=validation,
            )
        )

        # ----------------------------------------------------------
        # Targeted retrieval
        # ----------------------------------------------------------

        new_candidates = []

        for targeted_query in targeted_queries:

            results = retrieve_documents(
                query=targeted_query,
                top_k=adaptive_top_k,
                source=source,
            )

            new_candidates.extend(
                results
            )

        # ----------------------------------------------------------
        # Merge candidate pool
        # ----------------------------------------------------------

        candidates = merge_candidates(
            existing_documents=candidates,
            new_documents=new_candidates,
            max_candidates=40,
        )

        # ----------------------------------------------------------
        # Re-compose evidence
        # IMPORTANT:
        # compose_evidence does NOT accept query=
        # ----------------------------------------------------------

        evidence = compose_evidence(
            documents=candidates,
            query_context=query_context,
        )

        # ----------------------------------------------------------
        # Re-validate
        # ----------------------------------------------------------

        validation = validate_evidence(
            query=query,
            documents=evidence,
            query_context=query_context,
        )

        iteration += 1

        retrieval_history.append(
            {
                "iteration": iteration,
                "stage": "targeted_retrieval",
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

    # ==============================================================
    # ADAPTIVE STATUS
    # ==============================================================

    adaptive_triggered = (
        iteration > 1
    )

    adaptive_status = (
        "Triggered"
        if adaptive_triggered
        else "Not Required"
    )

    # ==============================================================
    # PHASE 5
    # EVIDENCE RE-RANKING
    # ==============================================================

    reranking_context = dict(
        query_context
    )

    reranking_context[
        "discovered_items"
    ] = validation.get(
        "discovered_items",
        [],
    )

    reranking_context[
        "validation"
    ] = validation

    # IMPORTANT:
    # Your current rerank_evidence() already returns
    # the final evidence set, so do not pass top_k here.

    reranked_evidence = rerank_evidence(
        query=query,
        documents=evidence,
        query_context=reranking_context,
    )

    # ==============================================================
    # PHASE 6
    # PERSONALIZED RAG GENERATION
    # ==============================================================

    generation_result = (
        generate_rag_response(
            query=query,
            evidence=reranked_evidence,
            query_context=query_context,
            personalization_context=(
                personalization_context
            ),
        )
    )

    # ==============================================================
    # FINAL OUTPUT
    # ==============================================================

    return {
        "query": query,

        "selected_source": source,

        # ----------------------------------------------------------
        # Query analysis
        # ----------------------------------------------------------

        "query_context": reranking_context,

        # ----------------------------------------------------------
        # Initial candidates
        # ----------------------------------------------------------

        "initial_candidates": (
            initial_candidates
        ),

        # ----------------------------------------------------------
        # Complete candidate pool
        # ----------------------------------------------------------

        "candidates": candidates,

        # ----------------------------------------------------------
        # Evidence before Phase 5
        # ----------------------------------------------------------

        "composed_evidence": evidence,

        # ----------------------------------------------------------
        # Final Phase 5 evidence
        # ----------------------------------------------------------

        "evidence": reranked_evidence,

        # Keep this alias because your current
        # test_generation.py uses final_evidence.

        "final_evidence": (
            reranked_evidence
        ),

        # ----------------------------------------------------------
        # Validation
        # ----------------------------------------------------------

        "validation": validation,

        # ----------------------------------------------------------
        # Adaptive retrieval
        # ----------------------------------------------------------

        "iterations": iteration,

        "adaptive_status": (
            adaptive_status
        ),

        "adaptive_retrieval": (
            adaptive_triggered
        ),

        "retrieval_history": (
            retrieval_history
        ),

        # ----------------------------------------------------------
        # Phase 7
        # ----------------------------------------------------------

        "personalization": (
            personalization_context
        ),

        # ----------------------------------------------------------
        # Phase 6
        # ----------------------------------------------------------

        "generation": (
            generation_result
        ),
    }
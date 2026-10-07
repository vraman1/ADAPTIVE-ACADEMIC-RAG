import re
from math import sqrt

from haystack import Document


# -------------------------------------------------------------------
# Basic text utilities
# -------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    return text.strip()


def tokenize(text: str) -> set[str]:
    """Return normalized word tokens."""
    normalized = normalize_text(text)

    if not normalized:
        return set()

    return set(normalized.split())


def document_text(document: Document) -> str:
    """Return searchable text from a Haystack document."""
    return document.content or ""


def document_key(document: Document) -> tuple:
    """Create a unique key for a document chunk."""
    return (
        document.meta.get("source"),
        document.meta.get("page_number"),
        document.meta.get("chunk_number"),
    )


# -------------------------------------------------------------------
# Query relevance
# -------------------------------------------------------------------

def calculate_query_relevance(
    query: str,
    document: Document,
) -> float:
    """
    Estimate how strongly a document matches the query.

    Uses token overlap rather than an additional embedding call.
    """

    query_tokens = tokenize(query)
    document_tokens = tokenize(
        document_text(document)
    )

    if not query_tokens or not document_tokens:
        return 0.0

    overlap = query_tokens.intersection(
        document_tokens
    )

    return min(
        len(overlap) / len(query_tokens),
        1.0,
    )


# -------------------------------------------------------------------
# Evidence-item matching
# -------------------------------------------------------------------

def item_match_score(
    item: str,
    document: Document,
) -> float:
    """
    Estimate whether a document contains information
    about a discovered evidence item.
    """

    item_tokens = tokenize(item)
    document_tokens = tokenize(
        document_text(document)
    )

    if not item_tokens or not document_tokens:
        return 0.0

    overlap = item_tokens.intersection(
        document_tokens
    )

    return min(
        len(overlap) / len(item_tokens),
        1.0,
    )


def calculate_item_coverage(
    document: Document,
    discovered_items: list[str],
) -> float:
    """
    Calculate how many Phase 4 discovered items
    are supported by this document.
    """

    if not discovered_items:
        return 0.0

    scores = []

    for item in discovered_items:
        score = item_match_score(
            item=item,
            document=document,
        )

        scores.append(score)

    if not scores:
        return 0.0

    return sum(scores) / len(scores)


# -------------------------------------------------------------------
# Description support
# -------------------------------------------------------------------

def calculate_description_support(
    document: Document,
    discovered_items: list[str],
) -> float:
    """
    Estimate whether the document provides explanatory
    information rather than only mentioning the item.
    """

    text = document_text(document)

    if not text:
        return 0.0

    normalized = normalize_text(text)

    description_terms = {
        "definition",
        "value",
        "role",
        "importance",
        "benefit",
        "benefits",
        "helps",
        "contributes",
        "supports",
        "improves",
        "manages",
        "provides",
        "includes",
        "because",
        "why",
        "how",
    }

    tokens = set(normalized.split())

    description_matches = (
        tokens.intersection(description_terms)
    )

    description_score = min(
        len(description_matches) / 4.0,
        1.0,
    )

    item_support = 0.0

    if discovered_items:
        matched_items = 0

        for item in discovered_items:
            if item_match_score(
                item,
                document,
            ) >= 0.5:
                matched_items += 1

        item_support = (
            matched_items / len(discovered_items)
        )

    return (
        0.6 * description_score
        + 0.4 * item_support
    )


# -------------------------------------------------------------------
# Requirement coverage
# -------------------------------------------------------------------

def calculate_requirement_coverage(
    document: Document,
    query_context: dict,
) -> float:
    """
    Calculate evidence coverage primarily from the
    discovered evidence items produced by Phase 4.

    Falls back to generic requirement matching when
    discovered items are unavailable.
    """

    discovered_items = query_context.get(
        "discovered_items",
        [],
    )

    if discovered_items:
        item_coverage = calculate_item_coverage(
            document=document,
            discovered_items=discovered_items,
        )

        description_support = (
            calculate_description_support(
                document=document,
                discovered_items=discovered_items,
            )
        )

        return (
            0.7 * item_coverage
            + 0.3 * description_support
        )

    requirements = query_context.get(
        "evidence_requirements",
        [],
    )

    if not requirements:
        return 0.0

    document_tokens = tokenize(
        document_text(document)
    )

    if not document_tokens:
        return 0.0

    scores = []

    for requirement in requirements:

        requirement_tokens = tokenize(
            requirement
        )

        if not requirement_tokens:
            continue

        overlap = requirement_tokens.intersection(
            document_tokens
        )

        score = min(
            len(overlap) / len(requirement_tokens),
            1.0,
        )

        scores.append(score)

    if not scores:
        return 0.0

    return sum(scores) / len(scores)


# -------------------------------------------------------------------
# Content quality
# -------------------------------------------------------------------

def calculate_content_quality(
    document: Document,
) -> float:
    """
    Estimate the quality of the text contained in
    an evidence chunk.
    """

    text = document_text(document)

    if not text:
        return 0.0

    length = len(text.strip())

    if length < 100:
        length_score = 0.4
    elif length < 300:
        length_score = 0.65
    elif length < 800:
        length_score = 0.85
    else:
        length_score = 1.0

    words = text.split()

    if not words:
        return 0.0

    unique_ratio = len(
        set(
            normalize_text(text).split()
        )
    ) / max(len(words), 1)

    uniqueness_score = min(
        unique_ratio,
        1.0,
    )

    return (
        0.75 * length_score
        + 0.25 * uniqueness_score
    )


# -------------------------------------------------------------------
# Structural quality
# -------------------------------------------------------------------

def calculate_structural_quality(
    document: Document,
) -> float:
    """
    Estimate whether the chunk has useful academic
    structure such as headings, lists, or multiple sentences.
    """

    text = document_text(document)

    if not text:
        return 0.0

    score = 0.5

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if len(lines) >= 3:
        score += 0.15

    if re.search(
        r"\b(definition|summary|key takeaways|"
        r"what|why|how|includes|role|benefits?)\b",
        text,
        flags=re.IGNORECASE,
    ):
        score += 0.15

    if re.search(
        r"(^|\n)\s*(\d+[\.\)]|[-•])\s+",
        text,
    ):
        score += 0.10

    if len(
        re.findall(
            r"[.!?]",
            text,
        )
    ) >= 3:
        score += 0.10

    return min(score, 1.0)


# -------------------------------------------------------------------
# Text similarity and redundancy
# -------------------------------------------------------------------

def calculate_text_similarity(
    document_a: Document,
    document_b: Document,
) -> float:
    """
    Calculate token-based Jaccard similarity.
    """

    tokens_a = tokenize(
        document_text(document_a)
    )

    tokens_b = tokenize(
        document_text(document_b)
    )

    if not tokens_a or not tokens_b:
        return 0.0

    intersection = tokens_a.intersection(
        tokens_b
    )

    union = tokens_a.union(tokens_b)

    if not union:
        return 0.0

    return len(intersection) / len(union)


def is_redundant(
    document: Document,
    selected_documents: list[Document],
    threshold: float = 0.80,
) -> bool:
    """
    Determine whether a document is too similar
    to already selected evidence.
    """

    for selected in selected_documents:

        similarity = calculate_text_similarity(
            document,
            selected,
        )

        if similarity >= threshold:
            return True

    return False


# -------------------------------------------------------------------
# Retrieval-score normalization
# -------------------------------------------------------------------

def calculate_retrieval_similarity(
    document: Document,
) -> float:
    """
    Normalize the original retrieval score into [0, 1].
    """

    score = document.score

    if score is None:
        return 0.0

    return max(
        0.0,
        min(float(score), 1.0),
    )


# -------------------------------------------------------------------
# Composite evidence score
# -------------------------------------------------------------------

def calculate_evidence_score(
    query: str,
    document: Document,
    query_context: dict,
) -> dict:
    """
    Calculate the Phase 5 composite evidence score.

    Weighting:
        30% retrieval similarity
        20% query relevance
        25% evidence coverage
        15% content quality
        10% structural quality
    """

    retrieval_similarity = (
        calculate_retrieval_similarity(
            document
        )
    )

    query_relevance = (
        calculate_query_relevance(
            query=query,
            document=document,
        )
    )

    evidence_coverage = (
        calculate_requirement_coverage(
            document=document,
            query_context=query_context,
        )
    )

    content_quality = (
        calculate_content_quality(
            document
        )
    )

    structural_quality = (
        calculate_structural_quality(
            document
        )
    )

    final_score = (
        0.30 * retrieval_similarity
        + 0.20 * query_relevance
        + 0.25 * evidence_coverage
        + 0.15 * content_quality
        + 0.10 * structural_quality
    )

    return {
        "evidence_score": round(
            final_score,
            4,
        ),
        "retrieval_similarity": round(
            retrieval_similarity,
            4,
        ),
        "query_relevance": round(
            query_relevance,
            4,
        ),
        "evidence_coverage": round(
            evidence_coverage,
            4,
        ),
        "content_quality": round(
            content_quality,
            4,
        ),
        "structural_quality": round(
            structural_quality,
            4,
        ),
    }


# -------------------------------------------------------------------
# Main reranking function
# -------------------------------------------------------------------

def rerank_evidence(
    query: str,
    documents: list[Document],
    query_context: dict,
    top_k: int = 7,
) -> list[Document]:
    """
    Re-rank composed evidence using the Phase 5
    composite evidence score.

    Parameters:
        query:
            Original user query.

        documents:
            Evidence selected by Phase 4.

        query_context:
            Query analysis + Phase 3/4 validation information.

        top_k:
            Maximum number of final evidence documents.

    Returns:
        Evidence documents sorted by final evidence score.
    """

    if not documents:
        return []

    scored_documents = []

    # ---------------------------------------------------------------
    # Calculate Phase 5 scores
    # ---------------------------------------------------------------

    for document in documents:

        scores = calculate_evidence_score(
            query=query,
            document=document,
            query_context=query_context,
        )

        # Store Phase 5 scores in document metadata.
        document.meta["evidence_score"] = (
            scores["evidence_score"]
        )

        document.meta["retrieval_similarity"] = (
            scores["retrieval_similarity"]
        )

        document.meta["retrieval_score"] = (
            document.score
        )

        document.meta["query_relevance"] = (
            scores["query_relevance"]
        )

        document.meta["evidence_coverage"] = (
            scores["evidence_coverage"]
        )

        document.meta["content_quality"] = (
            scores["content_quality"]
        )

        document.meta["structural_quality"] = (
            scores["structural_quality"]
        )

        scored_documents.append(
            (
                document,
                scores["evidence_score"],
            )
        )

    # ---------------------------------------------------------------
    # Sort by final composite evidence score
    # ---------------------------------------------------------------

    scored_documents.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    # ---------------------------------------------------------------
    # Select final evidence
    # ---------------------------------------------------------------

    selected_documents = []
    selected_keys = set()

    for document, score in scored_documents:

        key = document_key(document)

        # Avoid duplicate chunks.
        if key in selected_keys:
            continue

        # Avoid highly redundant evidence.
        if is_redundant(
            document=document,
            selected_documents=selected_documents,
        ):
            continue

        selected_documents.append(document)
        selected_keys.add(key)

        if len(selected_documents) >= top_k:
            break

    return selected_documents

# -------------------------------------------------------------------
# Quality report
# -------------------------------------------------------------------

def build_evidence_quality_report(
    documents: list[Document],
) -> dict:
    """
    Produce a summary of Phase 5 evidence quality.
    """

    if not documents:
        return {
            "evidence_count": 0,
            "average_evidence_score": 0.0,
            "minimum_evidence_score": 0.0,
            "maximum_evidence_score": 0.0,
        }

    scores = [
        document.meta.get(
            "evidence_score",
            0.0,
        )
        for document in documents
    ]

    return {
        "evidence_count": len(documents),
        "average_evidence_score": round(
            sum(scores) / len(scores),
            4,
        ),
        "minimum_evidence_score": round(
            min(scores),
            4,
        ),
        "maximum_evidence_score": round(
            max(scores),
            4,
        ),
    }
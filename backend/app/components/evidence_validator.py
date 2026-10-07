import re

from haystack import Document


# ============================================================
# TEXT UTILITIES
# ============================================================

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by",
    "for", "from", "how", "in", "is", "it", "of", "on",
    "or", "that", "the", "this", "to", "was", "what",
    "which", "with", "why",
}


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[\u2192\u2013\u2014]", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize(text: str) -> set[str]:
    text = normalize_text(text)

    if not text:
        return set()

    return {
        token
        for token in text.split()
        if token not in STOP_WORDS
    }


def document_text(document: Document) -> str:
    return document.content or ""


def document_key(document: Document):
    return (
        document.meta.get("source"),
        document.meta.get("page_number"),
        document.meta.get("chunk_number"),
    )


# ============================================================
# GENERIC STRUCTURAL RULES
# ============================================================

def looks_like_generic_heading(text: str) -> bool:
    normalized = normalize_text(text)

    if not normalized:
        return False

    patterns = [
        r"\bwhat we ll cover\b",
        r"\bwhat we will cover\b",
        r"\bwhat we ll discuss\b",
        r"\bwhat we will discuss\b",
        r"\broadmap\b",
        r"\boverview\b",
        r"\bintroduction\b",
        r"\bsummary\b",
        r"\bkey takeaways\b",
        r"\bquick recap\b",
        r"\brecap\b",
        r"\bbefore we start\b",
        r"\bbringing it together\b",
        r"\bconclusion\b",
        r"\bcontents\b",
        r"\btable of contents\b",
    ]

    return any(
        re.search(pattern, normalized)
        for pattern in patterns
    )


def looks_like_meta_heading(text: str) -> bool:
    """
    Reject subsection headings that describe an item rather
    than representing the item itself.
    """

    normalized = normalize_text(text)

    patterns = [
        r"^what .* includes$",
        r"^what .* means$",
        r"^why .* matters$",
        r"^why it matters$",
        r"^definition$",
        r"^examples?$",
        r"^sources? of ",
        r"^types? of ",
        r"^components? of ",
        r"^elements? of ",
        r"^benefits? of ",
        r"^advantages? of ",
        r"^disadvantages? of ",
        r"^how .* works$",
        r"^how .* works together$",
        r"^the .* chain$",
        r"^the .* process$",
        r"^the .* framework$",
    ]

    return any(
        re.search(pattern, normalized)
        for pattern in patterns
    )


def looks_like_list_introduction(text: str) -> bool:
    """
    Detect generic collection-introduction text.

    Examples:
        5 components
        five building blocks
        4 stages
        three factors
    """

    text = text.lower()

    number_words = {
        "one", "two", "three", "four", "five",
        "six", "seven", "eight", "nine", "ten",
    }

    collection_words = {
        "block", "blocks",
        "component", "components",
        "element", "elements",
        "part", "parts",
        "piece", "pieces",
        "stage", "stages",
        "step", "steps",
        "factor", "factors",
        "driver", "drivers",
        "method", "methods",
        "principle", "principles",
        "type", "types",
        "category", "categories",
        "item", "items",
        "area", "areas",
        "aspect", "aspects",
        "lever", "levers",
    }

    numeric = bool(
        re.search(
            r"\b\d+\s+"
            r"(?:blocks?|components?|elements?|parts?|"
            r"pieces?|stages?|steps?|factors?|drivers?|"
            r"methods?|principles?|types?|categories?|"
            r"items?|areas?|aspects?|levers?)\b",
            text,
        )
    )

    words = set(
        re.findall(r"\b[a-z]+\b", text)
    )

    written = bool(
        words.intersection(number_words)
        and words.intersection(collection_words)
    )

    return numeric or written


def clean_line(text: str) -> str:
    text = text.strip()

    text = re.sub(
        r"^[\-\u2022•▪◦\*\d\.\)\s]+",
        "",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def looks_like_heading(text: str) -> bool:
    if not text:
        return False

    text = text.strip()

    if len(text) < 2:
        return False

    if len(text) > 100:
        return False

    if text.endswith("."):
        return False

    if len(text.split()) > 10:
        return False

    if re.fullmatch(
        r"[\d\s\-./]+",
        text,
    ):
        return False

    return True


# ============================================================
# COLLECTION DETECTION
# ============================================================

def detect_collection_candidates(
    document: Document,
) -> list[list[dict]]:
    """
    Detect repeated heading -> description sequences.

    A collection is a sequence of at least three sibling
    topic-description pairs.

    This is intentionally generic.
    """

    lines = [
        clean_line(line)
        for line in document_text(document).splitlines()
        if line.strip()
    ]

    records = []

    index = 0

    while index < len(lines) - 1:

        title = lines[index]
        description = lines[index + 1]

        # -----------------------------------------------
        # Candidate title
        # -----------------------------------------------

        if (
            not looks_like_heading(title)
            or looks_like_generic_heading(title)
            or looks_like_meta_heading(title)
        ):
            index += 1
            continue

        # -----------------------------------------------
        # Candidate description
        # -----------------------------------------------

        if not description:
            index += 1
            continue

        if looks_like_list_introduction(
            description
        ):
            index += 1
            continue

        # A description should normally contain more
        # information than the heading.
        if len(description.split()) < 4:
            index += 1
            continue

        records.append(
            {
                "title": title,
                "description": description,
                "document": document,
                "document_key": document_key(
                    document
                ),
            }
        )

        index += 2

    # --------------------------------------------------------
    # Find runs of sibling structures.
    # --------------------------------------------------------

    collections = []

    current = []

    for record in records:

        if not current:

            current = [record]
            continue

        previous = current[-1]

        # Consecutive records from the same document form
        # a potential collection.
        if (
            record["document_key"]
            == previous["document_key"]
        ):
            current.append(record)

        else:

            if len(current) >= 3:
                collections.append(current)

            current = [record]

    if len(current) >= 3:
        collections.append(current)

    return collections


# ============================================================
# CROSS-EVIDENCE COLLECTION SCORING
# ============================================================

def candidate_support(
    title: str,
    documents: list[Document],
) -> dict:
    """
    Determine how strongly a title is supported elsewhere
    in the retrieved evidence.
    """

    title_tokens = tokenize(title)

    if not title_tokens:
        return {
            "documents": 0,
            "occurrences": 0,
            "score": 0.0,
        }

    occurrences = 0
    supporting_documents = set()

    for document in documents:

        content = document_text(document)

        content_normalized = normalize_text(
            content
        )

        title_normalized = normalize_text(
            title
        )

        # Direct phrase match.
        if title_normalized in content_normalized:

            occurrences += 1

            supporting_documents.add(
                document_key(document)
            )

            continue

        # Token match.
        content_tokens = tokenize(
            content
        )

        overlap = title_tokens.intersection(
            content_tokens
        )

        if (
            len(overlap)
            / len(title_tokens)
            >= 0.70
        ):

            occurrences += 1

            supporting_documents.add(
                document_key(document)
            )

    score = 0.0

    if occurrences >= 1:
        score += 0.30

    if occurrences >= 2:
        score += 0.25

    if len(supporting_documents) >= 2:
        score += 0.25

    return {
        "documents": len(
            supporting_documents
        ),
        "occurrences": occurrences,
        "score": score,
    }


def score_collection(
    collection: list[dict],
    documents: list[Document],
    required_count: int | None,
) -> float:
    """
    Score a whole collection rather than individual headings.

    This is the key mechanism preventing random PDF headings
    from being interpreted as the requested answer set.
    """

    score = 0.0

    # --------------------------------------------------------
    # Collection size.
    # --------------------------------------------------------

    collection_size = len(collection)

    if required_count is not None:

        if collection_size == required_count:
            score += 0.45

        elif collection_size >= required_count:
            score += 0.30

        elif collection_size >= 3:
            score += 0.10

    else:

        if collection_size >= 3:
            score += 0.25

    # --------------------------------------------------------
    # Individual item support.
    # --------------------------------------------------------

    supported = 0

    for record in collection:

        support = candidate_support(
            title=record["title"],
            documents=documents,
        )

        if support["score"] >= 0.30:
            supported += 1

    if collection_size > 0:

        support_ratio = (
            supported
            / collection_size
        )

        score += (
            0.40
            * support_ratio
        )

    # --------------------------------------------------------
    # Descriptive evidence.
    # --------------------------------------------------------

    descriptive_count = sum(
        1
        for record in collection
        if len(
            tokenize(
                record["description"]
            )
        ) >= 5
    )

    if collection_size > 0:

        description_ratio = (
            descriptive_count
            / collection_size
        )

        score += (
            0.15
            * description_ratio
        )

    return min(
        1.0,
        score,
    )


# ============================================================
# DISCOVER ITEMS FROM BEST COLLECTION
# ============================================================

def discover_items(
    documents: list[Document],
    query_context: dict,
) -> list[str]:
    """
    Discover the requested items by selecting the strongest
    sibling collection found in the evidence.

    This prevents isolated PDF headings or sentence fragments
    from being selected as requested items.
    """

    required_count = query_context.get(
        "required_count"
    )

    all_collections = []

    for document in documents:

        collections = detect_collection_candidates(
            document
        )

        all_collections.extend(
            collections
        )

    if not all_collections:
        return []

    # --------------------------------------------------------
    # Score every collection.
    # --------------------------------------------------------

    scored = []

    for collection in all_collections:

        score = score_collection(
            collection=collection,
            documents=documents,
            required_count=required_count,
        )

        scored.append(
            (
                score,
                collection,
            )
        )

    scored.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    best_score, best_collection = scored[0]

    # --------------------------------------------------------
    # If a requested count exists, prefer exactly that many
    # sibling items.
    # --------------------------------------------------------

    if required_count is not None:

        exact_matches = [
            collection
            for score, collection
            in scored
            if len(collection)
            == required_count
        ]

        if exact_matches:

            best_collection = max(
                exact_matches,
                key=lambda collection:
                    score_collection(
                        collection=collection,
                        documents=documents,
                        required_count=required_count,
                    ),
            )

    discovered = []

    for record in best_collection:

        title = record["title"]

        if (
            looks_like_generic_heading(
                title
            )
            or looks_like_meta_heading(
                title
            )
        ):
            continue

        if title not in discovered:
            discovered.append(title)

    if required_count is not None:

        discovered = discovered[
            :required_count
        ]

    return discovered


# ============================================================
# REQUIREMENT VALIDATION
# ============================================================

def requirement_is_generic(
    requirement: str,
) -> bool:

    normalized = normalize_text(
        requirement
    )

    generic_phrases = {
        "main concept",
        "supporting explanation",
        "key concept",
        "key points",
        "main ideas",
        "relevant information",
        "broader supporting evidence",
        "assignment relevant supporting evidence",
        "important exam focused information",
    }

    if normalized in generic_phrases:
        return True

    return len(
        tokenize(requirement)
    ) <= 2


def requirement_coverage(
    requirement: str,
    documents: list[Document],
) -> float:

    requirement_tokens = tokenize(
        requirement
    )

    if not requirement_tokens:
        return (
            1.0
            if documents
            else 0.0
        )

    evidence_tokens = set()

    for document in documents:

        evidence_tokens.update(
            tokenize(
                document_text(document)
            )
        )

    overlap = requirement_tokens.intersection(
        evidence_tokens
    )

    return (
        len(overlap)
        / len(requirement_tokens)
    )


def is_descriptive_requirement(
    requirement: str,
) -> bool:

    tokens = tokenize(
        requirement
    )

    descriptive_terms = {
        "describe",
        "description",
        "explain",
        "explanation",
        "role",
        "purpose",
        "function",
        "importance",
        "significance",
        "benefit",
        "benefits",
        "use",
        "uses",
        "application",
        "applications",
        "impact",
        "effect",
        "effects",
    }

    return bool(
        tokens.intersection(
            descriptive_terms
        )
    )


def supports_descriptive_requirement(
    requirement: str,
    discovered_items: list[str],
    documents: list[Document],
) -> bool:
    """
    Check that discovered items have supporting evidence.
    """

    if not discovered_items:
        return False

    if not documents:
        return False

    if not is_descriptive_requirement(
        requirement
    ):
        return False

    evidence_text = " ".join(
        document_text(document)
        for document in documents
    )

    evidence_normalized = normalize_text(
        evidence_text
    )

    supported = 0

    for item in discovered_items:

        normalized_item = normalize_text(
            item
        )

        if not normalized_item:
            continue

        if normalized_item in evidence_normalized:

            supported += 1
            continue

        item_tokens = tokenize(
            item
        )

        evidence_tokens = tokenize(
            evidence_text
        )

        if not item_tokens:
            continue

        overlap = item_tokens.intersection(
            evidence_tokens
        )

        ratio = (
            len(overlap)
            / len(item_tokens)
        )

        if ratio >= 0.60:
            supported += 1

    return (
        supported
        / len(discovered_items)
    ) >= 0.80


# ============================================================
# REQUIREMENT COVERAGE
# ============================================================

def detect_requirement_coverage(
    documents: list[Document],
    query_context: dict,
) -> dict:

    requirements = query_context.get(
        "evidence_requirements",
        [],
    )

    required_count = query_context.get(
        "required_count"
    )

    discovered_items = discover_items(
        documents=documents,
        query_context=query_context,
    )

    requirement_scores = {}

    missing_requirements = []

    # --------------------------------------------------------
    # Semantic requirements.
    # --------------------------------------------------------

    for requirement in requirements:

        if requirement_is_generic(
            requirement
        ):

            score = (
                1.0
                if documents
                else 0.0
            )

        elif supports_descriptive_requirement(
            requirement=requirement,
            discovered_items=discovered_items,
            documents=documents,
        ):

            score = 1.0

        else:

            score = requirement_coverage(
                requirement=requirement,
                documents=documents,
            )

        requirement_scores[
            requirement
        ] = score

        if score < 0.30:

            missing_requirements.append(
                requirement
            )

    # --------------------------------------------------------
    # Requested item count.
    # --------------------------------------------------------

    if required_count is not None:

        count_requirement = (
            f"{required_count} requested items"
        )

        if len(discovered_items) < required_count:

            if (
                count_requirement
                not in missing_requirements
            ):
                missing_requirements.append(
                    count_requirement
                )

    # --------------------------------------------------------
    # Coverage score.
    # --------------------------------------------------------

    if requirement_scores:

        semantic_scores = list(
            requirement_scores.values()
        )

        coverage = (
            sum(semantic_scores)
            / len(semantic_scores)
        )

    else:

        coverage = (
            1.0
            if documents
            else 0.0
        )

    if required_count is not None:

        count_coverage = min(
            1.0,
            len(discovered_items)
            / required_count,
        )

        coverage = (
            coverage * 0.70
            + count_coverage * 0.30
        )

    coverage = round(
        coverage,
        3,
    )

    return {
        "coverage": coverage,
        "coverage_score": coverage,
        "missing_requirements": (
            missing_requirements
        ),
        "discovered_items": (
            discovered_items
        ),
        "requirement_scores": (
            requirement_scores
        ),
    }


# ============================================================
# MAIN VALIDATOR
# ============================================================

def validate_evidence(
    query: str,
    documents: list[Document],
    query_context: dict,
) -> dict:
    """
    Main evidence validation entry point.

    The validator:
        1. Discovers a coherent item collection.
        2. Checks semantic evidence requirements.
        3. Checks requested item count.
        4. Reports missing evidence for adaptive retrieval.
    """

    # --------------------------------------------------------
    # No evidence.
    # --------------------------------------------------------

    if not documents:

        missing_requirements = (
            query_context.get(
                "evidence_requirements",
                [],
            )
        )

        return {
            "sufficient": False,
            "coverage": 0.0,
            "coverage_score": 0.0,
            "missing_requirements": (
                missing_requirements
            ),
            "missing_parts": [],
            "discovered_items": [],
            "requirement_scores": {},
            "evidence_count": 0,
        }

    # --------------------------------------------------------
    # Analyze evidence.
    # --------------------------------------------------------

    result = detect_requirement_coverage(
        documents=documents,
        query_context=query_context,
    )

    coverage = result[
        "coverage"
    ]

    missing_requirements = result[
        "missing_requirements"
    ]

    discovered_items = result[
        "discovered_items"
    ]

    required_count = query_context.get(
        "required_count"
    )

    # --------------------------------------------------------
    # Count sufficiency.
    # --------------------------------------------------------

    count_sufficient = True

    if required_count is not None:

        count_sufficient = (
            len(discovered_items)
            >= required_count
        )

    # --------------------------------------------------------
    # Semantic sufficiency.
    # --------------------------------------------------------

    semantic_sufficient = (
        len(missing_requirements) == 0
    )

    sufficient = (
        semantic_sufficient
        and count_sufficient
    )

    # --------------------------------------------------------
    # Missing parts.
    # --------------------------------------------------------

    missing_parts = []

    if (
        required_count is not None
        and len(discovered_items)
        < required_count
    ):

        missing_parts.append(
            f"additional item(s) "
            f"needed to reach {required_count}"
        )

    # --------------------------------------------------------
    # Final result.
    # --------------------------------------------------------

    return {
        "sufficient": sufficient,
        "coverage": coverage,
        "coverage_score": coverage,
        "missing_requirements": (
            missing_requirements
        ),
        "missing_parts": missing_parts,
        "discovered_items": discovered_items,
        "requirement_scores": (
            result["requirement_scores"]
        ),
        "evidence_count": len(documents),
    }
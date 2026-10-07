import re

from haystack import Document


def document_key(document: Document) -> tuple:
    return (
        document.meta.get("source"),
        document.meta.get("page_number"),
        document.meta.get("chunk_number"),
    )


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def is_duplicate(
    document: Document,
    selected: list[Document],
) -> bool:

    current = normalize_text(
        document.content
    )

    for existing in selected:

        existing_text = normalize_text(
            existing.content
        )

        if current == existing_text:
            return True

        if (
            len(current) >= 150
            and len(existing_text) >= 150
        ):
            if (
                current[:300]
                in existing_text
            ):
                return True

    return False


def detect_explicit_parts(
    document: Document,
) -> set[int]:

    text = document.content.lower()

    patterns = [
        r"\b(?:tier|part|section|stage|step)\s*[-–:]?\s*(\d+)\b"
    ]

    parts = set()

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
        )

        for number in matches:
            parts.add(int(number))

    return parts


def requirement_matches_document(
    requirement: str,
    document: Document,
) -> bool:
    """
    Determine whether a document chunk appears
    to support an evidence requirement.

    This is intentionally lightweight in Phase 2.
    We use textual overlap rather than introducing
    another embedding model or LLM call.
    """

    requirement_words = {
        word
        for word in re.findall(
            r"[a-zA-Z]{4,}",
            requirement.lower(),
        )
    }

    if not requirement_words:
        return False

    document_text = normalize_text(
        document.content
    )

    matched_words = sum(
        1
        for word in requirement_words
        if word in document_text
    )

    return matched_words >= max(
        1,
        len(requirement_words) // 2,
    )


def calculate_requirement_coverage(
    documents: list[Document],
    query_context: dict,
) -> dict:

    requirements = query_context.get(
        "evidence_requirements",
        [],
    )

    if not requirements:
        return {
            "covered_requirements": [],
            "missing_requirements": [],
            "coverage_score": 1.0,
        }

    covered = []
    missing = []

    for requirement in requirements:

        found = any(
            requirement_matches_document(
                requirement,
                document,
            )
            for document in documents
        )

        if found:
            covered.append(requirement)
        else:
            missing.append(requirement)

    coverage = (
        len(covered) / len(requirements)
        if requirements
        else 1.0
    )

    return {
        "covered_requirements": covered,
        "missing_requirements": missing,
        "coverage_score": round(
            coverage,
            3,
        ),
    }


def compose_evidence(
    documents: list[Document],
    query_context: dict,
) -> list[Document]:

    if not documents:
        return []

    ranked = sorted(
        documents,
        key=lambda document: (
            document.score
            if document.score is not None
            else 0
        ),
        reverse=True,
    )

    selected = []
    selected_keys = set()

    requirements = query_context.get(
        "evidence_requirements",
        [],
    )

    # --------------------------------------------------
    # PHASE 2: Requirement-aware composition
    # --------------------------------------------------

    if requirements:

        # First pass:
        # Try to select evidence that covers
        # different requirements.
        for requirement in requirements:

            for document in ranked:

                key = document_key(
                    document
                )

                if key in selected_keys:
                    continue

                if is_duplicate(
                    document,
                    selected,
                ):
                    continue

                if requirement_matches_document(
                    requirement,
                    document,
                ):

                    selected.append(
                        document
                    )

                    selected_keys.add(
                        key
                    )

                    break

        # Second pass:
        # Fill remaining evidence slots using
        # high-scoring complementary documents.
        required_count = query_context.get(
            "required_count"
        )

        if required_count:
            target_size = min(
                max(required_count, 3) + 2,
                10,
            )
        else:
            target_size = 5

        for document in ranked:

            key = document_key(
                document
            )

            if key in selected_keys:
                continue

            if is_duplicate(
                document,
                selected,
            ):
                continue

            selected.append(
                document
            )

            selected_keys.add(
                key
            )

            if len(selected) >= target_size:
                break

        return selected

    # --------------------------------------------------
    # Fallback for queries without requirements
    # --------------------------------------------------

    intent = query_context.get(
        "intent",
        "general",
    )

    evidence_limits = {
        "definition": 3,
        "comparison": 6,
        "summarization": 5,
        "explanation": 5,
        "example": 5,
        "general": 5,
    }

    limit = evidence_limits.get(
        intent,
        5,
    )

    for document in ranked:

        key = document_key(
            document
        )

        if key in selected_keys:
            continue

        if is_duplicate(
            document,
            selected,
        ):
            continue

        selected.append(
            document
        )

        selected_keys.add(
            key
        )

        if len(selected) >= limit:
            break

    return selected
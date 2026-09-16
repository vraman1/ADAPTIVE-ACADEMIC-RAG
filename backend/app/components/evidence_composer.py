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


def is_duplicate(document: Document, selected: list[Document]) -> bool:
    current = normalize_text(document.content)

    for existing in selected:
        existing_text = normalize_text(existing.content)

        if current == existing_text:
            return True

        if len(current) >= 150 and len(existing_text) >= 150:
            if current[:300] in existing_text:
                return True

    return False


def detect_explicit_parts(document: Document) -> set[int]:
    text = document.content.lower()

    patterns = [
        r"\b(?:tier|part|section|stage|step)\s*[-–:]?\s*(\d+)\b",
    ]

    parts = set()

    for pattern in patterns:
        matches = re.findall(pattern, text)

        for number in matches:
            parts.add(int(number))

    return parts


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

    intent = query_context.get("intent", "general")
    required_count = query_context.get("required_count")

    selected = []
    selected_keys = set()

    # ---------------------------------------------------------
    # MULTI-PART QUERY
    # ---------------------------------------------------------

    if required_count:

        for part_number in range(1, required_count + 1):

            matching = [
                document
                for document in ranked
                if part_number in detect_explicit_parts(document)
            ]

            for candidate in matching:

                key = document_key(candidate)

                if (
                    key not in selected_keys
                    and not is_duplicate(candidate, selected)
                ):
                    selected.append(candidate)
                    selected_keys.add(key)
                    break

        # Fill remaining evidence with highest-ranked documents

        for document in ranked:

            key = document_key(document)

            if key in selected_keys:
                continue

            if is_duplicate(document, selected):
                continue

            selected.append(document)
            selected_keys.add(key)

            if len(selected) >= min(required_count + 2, 10):
                break

        return selected

    # ---------------------------------------------------------
    # NORMAL QUERY
    # ---------------------------------------------------------

    evidence_limits = {
        "definition": 3,
        "comparison": 6,
        "summarization": 5,
        "explanation": 5,
        "example": 5,
        "general": 5,
    }

    limit = evidence_limits.get(intent, 5)

    for document in ranked:

        key = document_key(document)

        if key in selected_keys:
            continue

        if is_duplicate(document, selected):
            continue

        selected.append(document)
        selected_keys.add(key)

        if len(selected) >= limit:
            break

    return selected
import re

from haystack import Document


def _document_parts(
    document: Document,
) -> set[int]:

    text = document.content.lower()

    patterns = [
        r"\b(?:tier|part|section|stage|step)\s*[-–:]?\s*(\d+)\b",
    ]

    parts = set()

    for pattern in patterns:

        parts.update(
            int(number)
            for number in re.findall(
                pattern,
                text,
            )
        )

    return parts


def _document_key(
    document: Document,
) -> tuple:

    return (
        document.meta.get("source"),
        document.meta.get("page_number"),
        document.meta.get("chunk_number"),
    )


def _is_duplicate(
    document,
    selected,
) -> bool:

    normalized = " ".join(
        document.content.lower().split()
    )

    for existing in selected:

        existing_text = " ".join(
            existing.content.lower().split()
        )

        if normalized == existing_text:
            return True

        shorter = min(
            len(normalized),
            len(existing_text),
        )

        if shorter >= 150:

            common_prefix = normalized[:300]

            if (
                common_prefix
                and common_prefix in existing_text
            ):

                return True

    return False


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

    required_count = query_context.get(
        "required_count"
    )

    intent = query_context.get(
        "intent"
    )

    # Multi-part questions
    if required_count:

        selected = []

        selected_keys = set()

        for part_number in range(
            1,
            required_count + 1,
        ):

            matching = [
                document
                for document in ranked
                if part_number
                in _document_parts(document)
            ]

            if matching:

                for candidate in matching:

                    key = _document_key(
                        candidate
                    )

                    if (
                        key not in selected_keys
                        and not _is_duplicate(
                            candidate,
                            selected,
                        )
                    ):

                        selected.append(
                            candidate
                        )

                        selected_keys.add(
                            key
                        )

                        break

        # Add complementary evidence.
        for document in ranked:

            key = _document_key(
                document
            )

            if (
                key in selected_keys
                or _is_duplicate(
                    document,
                    selected,
                )
            ):

                continue

            selected.append(
                document
            )

            selected_keys.add(
                key
            )

            if len(selected) >= min(
                max(required_count + 2, 6),
                8,
            ):

                break

        return selected

    limits = {
        "definition": 2,
        "summarization": 3,
        "explanation": 4,
        "comparison": 5,
        "example": 4,
        "general": 3,
    }

    limit = limits.get(
        intent,
        3,
    )

    selected = []

    seen = set()

    for document in ranked:

        key = _document_key(
            document
        )

        if (
            key in seen
            or _is_duplicate(
                document,
                selected,
            )
        ):

            continue

        seen.add(key)

        selected.append(
            document
        )

        if len(selected) >= limit:
            break

    return selected
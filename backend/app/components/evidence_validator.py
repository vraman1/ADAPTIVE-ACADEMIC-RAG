import re


GENERIC_PART_PATTERNS = [
    r"\b(?:tier|part|section|stage|step)\s*[-–:]?\s*(\d+)\b",
]


def _document_key(document):

    return (
        document.meta.get("source"),
        document.meta.get("page_number"),
        document.meta.get("chunk_number"),
    )


def _explicit_parts(documents):

    parts = {}

    for document in documents:

        text = document.content.lower()

        for pattern in GENERIC_PART_PATTERNS:

            for match in re.finditer(
                pattern,
                text,
            ):

                number = int(
                    match.group(1)
                )

                parts.setdefault(
                    number,
                    document,
                )

    return parts


def _heading_candidates(
    documents,
):

    """
    Detect likely headings without
    assuming a specific subject.
    """

    candidates = []

    for document in documents:

        lines = [
            re.sub(
                r"^[\s•●▪◦\-–—\d.)]+",
                "",
                line,
            ).strip()
            for line in document.content.splitlines()
        ]

        for line in lines:

            if not line:
                continue

            if len(line) > 100:
                continue

            words = line.split()

            if not 1 <= len(words) <= 12:
                continue

            # Ordinary sentences are less likely to be headings.
            if line.endswith(
                (".", "?", "!")
            ):

                continue

            title_case = sum(
                word[:1].isupper()
                for word in words
                if word
            )

            all_caps = (
                line.upper() == line
                and any(
                    ch.isalpha()
                    for ch in line
                )
            )

            parenthesized = (
                "(" in line
                and ")" in line
            )

            if (
                all_caps
                or title_case
                >= max(
                    1,
                    int(
                        len(words)
                        * 0.6
                    ),
                )
                or parenthesized
            ):

                candidates.append(
                    (
                        document,
                        line.lower(),
                    )
                )

    return candidates


def _detect_ordered_parts(
    documents,
    required_count,
):

    explicit = _explicit_parts(
        documents
    )

    if len(explicit) >= required_count:

        return {
            n: explicit[n]
            for n in range(
                1,
                required_count + 1,
            )
            if n in explicit
        }

    heading_docs = []

    seen_keys = set()

    for document, _heading in _heading_candidates(
        documents
    ):

        key = _document_key(
            document
        )

        if key not in seen_keys:

            seen_keys.add(key)

            heading_docs.append(
                document
            )

    heading_docs.sort(
        key=lambda document: (
            document.meta.get(
                "page_number",
                0,
            ),
            document.meta.get(
                "chunk_number",
                0,
            ),
        )
    )

    detected = dict(
        explicit
    )

    next_number = 1

    for document in heading_docs:

        while next_number in detected:
            next_number += 1

        if next_number > required_count:
            break

        detected[
            next_number
        ] = document

        next_number += 1

    return {
        n: detected[n]
        for n in range(
            1,
            required_count + 1,
        )
        if n in detected
    }


def _score_threshold(
    documents,
):

    scores = [
        document.score
        for document in documents
        if document.score is not None
    ]

    if not scores:
        return 0.55

    top_score = max(
        scores
    )

    return max(
        0.55,
        top_score * 0.72,
    )


def filter_relevant_documents(
    documents,
):

    if not documents:
        return []

    threshold = _score_threshold(
        documents
    )

    filtered = [
        document
        for document in documents
        if (
            document.score is None
            or document.score >= threshold
        )
    ]

    return filtered


def validate_evidence(
    query: str,
    documents,
    query_context: dict,
) -> dict:

    if not documents:

        return {
            "sufficient": False,
            "coverage_score": 0.0,
            "average_score": 0.0,
            "covered_parts": [],
            "missing_parts": [],
            "reason": "No evidence retrieved.",
        }

    documents = filter_relevant_documents(
        documents
    )

    scores = [
        document.score
        for document in documents
        if document.score is not None
    ]

    average_score = (
        sum(scores) / len(scores)
        if scores
        else 0.0
    )

    required_count = query_context.get(
        "required_count"
    )

    if required_count:

        detected_parts = _detect_ordered_parts(
            documents,
            required_count,
        )

        covered_parts = [
            number
            for number in range(
                1,
                required_count + 1,
            )
            if number in detected_parts
        ]

        missing_parts = [
            number
            for number in range(
                1,
                required_count + 1,
            )
            if number not in detected_parts
        ]

        coverage = (
            len(covered_parts)
            / required_count
        )

        sufficient = (
            coverage >= 1.0
            and average_score >= 0.55
        )

        return {
            "sufficient": sufficient,
            "coverage_score": round(
                coverage,
                3,
            ),
            "average_score": round(
                average_score,
                3,
            ),
            "covered_parts": covered_parts,
            "missing_parts": missing_parts,
            "reason": (
                "All requested parts are covered."
                if sufficient
                else f"Missing parts: {missing_parts}"
            ),
        }

    query_words = {
        word
        for word in re.findall(
            r"[a-zA-Z]{4,}",
            query.lower(),
        )
        if word not in {
            "what",
            "what's",
            "explain",
            "define",
            "definition",
            "describe",
            "does",
            "with",
            "from",
            "about",
            "this",
            "that",
            "using",
        }
    }

    combined_text = " ".join(
        document.content.lower()
        for document in documents
    )

    matched = sum(
        1
        for word in query_words
        if word in combined_text
    )

    coverage = (
        matched / len(query_words)
        if query_words
        else 1.0
    )

    sufficient = (
        coverage >= 0.5
        and average_score >= 0.55
    )

    return {
        "sufficient": sufficient,
        "coverage_score": round(
            coverage,
            3,
        ),
        "average_score": round(
            average_score,
            3,
        ),
        "covered_parts": [],
        "missing_parts": [],
        "reason": (
            "Evidence is sufficient."
            if sufficient
            else "Evidence coverage is insufficient."
        ),
    }
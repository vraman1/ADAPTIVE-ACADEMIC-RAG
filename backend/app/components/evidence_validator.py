import re


# ============================================================
# DOCUMENT HELPERS
# ============================================================

def document_key(document):
    return (
        document.meta.get("source"),
        document.meta.get("page_number"),
        document.meta.get("chunk_number"),
    )


def calculate_average_score(documents):
    scores = [
        document.score
        for document in documents
        if document.score is not None
    ]

    if not scores:
        return 0.0

    return sum(scores) / len(scores)


# ============================================================
# NUMBERED PART DETECTION
# ============================================================

def detect_parts(documents):
    parts = {}

    patterns = [
        r"\b(?:tier|part|section|stage|step)\s*[-–:]?\s*(\d+)\b"
    ]

    for document in documents:
        text = document.content.lower()

        for pattern in patterns:
            for match in re.finditer(pattern, text):
                number = int(match.group(1))

                if number not in parts:
                    parts[number] = document

    return parts


# ============================================================
# CLV BUILDING BLOCK DETECTION
# ============================================================

CLV_BUILDING_BLOCKS = {
    1: [
        "crm in b2b",
        "b2b crm",
    ],

    2: [
        "business reference value",
        "reference value",
        "brv",
    ],

    3: [
        "customer knowledge value",
        "knowledge value",
    ],

    4: [
        "multi-channel analysis",
        "multi-channel management",
        "multi channel analysis",
        "multi channel management",
    ],

    5: [
        "employee engagement",
    ],
}


def detect_clv_building_blocks(documents):
    """
    Detect the five CLV building blocks from the actual
    terminology used in the academic material.
    """

    detected = {}

    for document in documents:

        text = document.content.lower()

        for number, keywords in CLV_BUILDING_BLOCKS.items():

            if number in detected:
                continue

            for keyword in keywords:

                if keyword in text:
                    detected[number] = document
                    break

    return detected


# ============================================================
# KEYWORD COVERAGE
# ============================================================

def calculate_keyword_coverage(query, documents):

    query_words = {
        word
        for word in re.findall(
            r"[a-zA-Z]{4,}",
            query.lower()
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
            "please",
            "help",
            "tell",
            "give",
            "five",
            "building",
            "blocks",
        }
    }

    if not query_words:
        return 1.0

    combined_text = " ".join(
        document.content.lower()
        for document in documents
    )

    matched = sum(
        1
        for word in query_words
        if word in combined_text
    )

    return matched / len(query_words)


# ============================================================
# MAIN VALIDATION FUNCTION
# ============================================================

def validate_evidence(
    query: str,
    documents,
    query_context: dict
) -> dict:

    # ------------------------------------------------------------
    # No evidence
    # ------------------------------------------------------------
    if not documents:

        return {
            "sufficient": False,
            "coverage_score": 0.0,
            "average_score": 0.0,
            "covered_parts": [],
            "missing_parts": [],
            "reason": "No evidence retrieved.",
        }

    average_score = calculate_average_score(documents)

    required_count = query_context.get("required_count")

    # ------------------------------------------------------------
    # Five CLV building blocks
    # ------------------------------------------------------------
    if (
        required_count == 5
        and "building block" in query.lower()
        and (
            "customer lifetime value" in query.lower()
            or "clv" in query.lower()
        )
    ):

        detected_blocks = detect_clv_building_blocks(
            documents
        )

        covered_parts = [
            number
            for number in range(1, 6)
            if number in detected_blocks
        ]

        missing_parts = [
            number
            for number in range(1, 6)
            if number not in detected_blocks
        ]

        coverage = len(covered_parts) / 5

        sufficient = (
            coverage >= 1.0
            and average_score >= 0.55
        )

        return {
            "sufficient": sufficient,
            "coverage_score": round(coverage, 3),
            "average_score": round(average_score, 3),
            "covered_parts": covered_parts,
            "missing_parts": missing_parts,
            "reason": (
                "All five CLV building blocks are covered."
                if sufficient
                else f"Missing building blocks: {missing_parts}"
            ),
        }

    # ------------------------------------------------------------
    # Generic numbered items
    # ------------------------------------------------------------
    if required_count:

        detected_parts = detect_parts(documents)

        covered_parts = [
            number
            for number in range(1, required_count + 1)
            if number in detected_parts
        ]

        missing_parts = [
            number
            for number in range(1, required_count + 1)
            if number not in detected_parts
        ]

        coverage = (
            len(covered_parts) / required_count
        )

        sufficient = (
            coverage >= 1.0
            and average_score >= 0.55
        )

        return {
            "sufficient": sufficient,
            "coverage_score": round(coverage, 3),
            "average_score": round(average_score, 3),
            "covered_parts": covered_parts,
            "missing_parts": missing_parts,
            "reason": (
                "All requested parts are covered."
                if sufficient
                else f"Missing parts: {missing_parts}"
            ),
        }

    # ------------------------------------------------------------
    # General query
    # ------------------------------------------------------------
    keyword_coverage = calculate_keyword_coverage(
        query,
        documents
    )

    sufficient = (
        keyword_coverage >= 0.60
        and average_score >= 0.55
    )

    return {
        "sufficient": sufficient,
        "coverage_score": round(
            keyword_coverage,
            3
        ),
        "average_score": round(
            average_score,
            3
        ),
        "covered_parts": [],
        "missing_parts": [],
        "reason": (
            "Evidence is sufficient."
            if sufficient
            else "Evidence coverage is insufficient."
        ),
    }
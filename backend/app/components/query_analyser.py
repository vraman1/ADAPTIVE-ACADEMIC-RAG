import re


DEFINITION_PATTERNS = [
    r"\bdefine\b",
    r"\bdefinition of\b",
    r"\bmeaning of\b",
    r"\bwhat is\b",
    r"\bwhat's\b",
]


COMPARISON_PATTERNS = [
    r"\bcompare\b",
    r"\bcomparison\b",
    r"\bdifference\b",
    r"\bdifferences\b",
    r"\bdifferentiate\b",
    r"\bcontrast\b",
    r"\bversus\b",
    r"\bvs\.?\b",
]


SUMMARY_PATTERNS = [
    r"\bsummarize\b",
    r"\bsummarise\b",
    r"\bsummary\b",
    r"\bbriefly\b",
    r"\bkey points\b",
]


EXPLANATION_PATTERNS = [
    r"\bexplain\b",
    r"\bdescribe\b",
    r"\bhow does\b",
    r"\bhow do\b",
    r"\bwhy\b",
    r"\badvantages?\b",
    r"\bbenefits?\b",
    r"\bfeatures?\b",
    r"\bimportance\b",
    r"\brole of\b",
]


EXAMPLE_PATTERNS = [
    r"\bexample\b",
    r"\bexamples\b",
    r"\billustrate\b",
    r"\buse cases?\b",
    r"\bapplications?\b",
]


def _matches_any(
    text: str,
    patterns: list[str],
) -> bool:

    return any(
        re.search(pattern, text)
        for pattern in patterns
    )


def analyze_query(
    query: str,
) -> dict:

    q = query.lower().strip()

    if not q:

        return {
            "query": query,
            "intent": "general",
            "complexity": "low",
            "multi_concept": False,
            "required_count": None,
            "learning_context": "conceptual_learning",
        }

    # Order matters.
    # Comparison should be detected before generic
    # explanation/definition patterns.

    if _matches_any(
        q,
        COMPARISON_PATTERNS,
    ):

        intent = "comparison"

    elif _matches_any(
        q,
        SUMMARY_PATTERNS,
    ):

        intent = "summarization"

    elif _matches_any(
        q,
        EXAMPLE_PATTERNS,
    ):

        intent = "example"

    elif _matches_any(
        q,
        EXPLANATION_PATTERNS,
    ):

        intent = "explanation"

    elif _matches_any(
        q,
        DEFINITION_PATTERNS,
    ):

        intent = "definition"

    else:

        intent = "general"

    word_count = len(
        q.split()
    )

    if word_count <= 8:

        complexity = "low"

    elif word_count <= 18:

        complexity = "medium"

    else:

        complexity = "high"

    number_match = re.search(
        r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
        r"(tiers?|parts?|steps?|stages?|components?|points?|factors?|"
        r"methods?|types?|features?|principles?|items?|ways?|reasons?)\b",
        q,
    )

    number_map = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    required_count = None

    if number_match:

        value = number_match.group(1)

        required_count = number_map.get(
            value,
            int(value)
            if value.isdigit()
            else None,
        )

    multi_concept = (
        required_count is not None
        or bool(
            re.search(
                r"\b(and|between|multiple|several|both)\b",
                q,
            )
        )
        or intent == "comparison"
    )

    if re.search(
        r"\b(exam|revision|study|prepare|preparation|important questions?)\b",
        q,
    ):

        learning_context = "exam_preparation"

    elif re.search(
        r"\b(assignment|report|project|coursework)\b",
        q,
    ):

        learning_context = "assignment"

    elif re.search(
        r"\b(research|paper|literature|research question)\b",
        q,
    ):

        learning_context = "research"

    else:

        learning_context = "conceptual_learning"

    return {
        "query": query,
        "intent": intent,
        "complexity": complexity,
        "multi_concept": multi_concept,
        "required_count": required_count,
        "learning_context": learning_context,
    }
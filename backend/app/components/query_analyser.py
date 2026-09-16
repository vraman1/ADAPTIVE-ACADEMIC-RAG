import re


def detect_intent(query: str) -> str:
    q = query.lower()

    if re.search(
        r"\b(compare|comparison|difference|differences|differentiate|"
        r"contrast|versus|vs\.?)\b",
        q,
    ):
        return "comparison"

    if re.search(
        r"\b(summarize|summarise|summary|briefly|key points)\b",
        q,
    ):
        return "summarization"

    if re.search(
        r"\b(example|examples|illustrate|use cases?|applications?)\b",
        q,
    ):
        return "example"

    if re.search(
        r"\b(explain|describe|how does|how do|why|advantages?|"
        r"benefits?|features?|importance|role of)\b",
        q,
    ):
        return "explanation"

    if re.search(
        r"\b(define|definition of|meaning of|what is|what's)\b",
        q,
    ):
        return "definition"

    return "general"


def detect_learning_context(query: str) -> str:
    q = query.lower()

    if re.search(
        r"\b(exam|revision|study|prepare|preparation|important questions?)\b",
        q,
    ):
        return "exam_preparation"

    if re.search(
        r"\b(assignment|report|project|coursework)\b",
        q,
    ):
        return "assignment"

    if re.search(
        r"\b(research|paper|literature|research question)\b",
        q,
    ):
        return "research"

    return "conceptual_learning"


def detect_required_count(query: str):
    q = query.lower()

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

    pattern = (
        r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
        r"(tiers?|parts?|steps?|stages?|components?|points?|factors?|"
        r"methods?|types?|features?|principles?|items?|ways?|reasons?|"
        r"building blocks?|elements?|aspects?|characteristics?)\b"
    )

    match = re.search(pattern, q)

    if not match:
        return None

    value = match.group(1)

    if value.isdigit():
        return int(value)

    return number_map.get(value)


def analyze_query(query: str) -> dict:
    query = query.strip()

    if not query:
        return {
            "query": query,
            "intent": "general",
            "complexity": "low",
            "multi_concept": False,
            "required_count": None,
            "learning_context": "conceptual_learning",
        }

    intent = detect_intent(query)
    learning_context = detect_learning_context(query)
    required_count = detect_required_count(query)

    word_count = len(query.split())

    if word_count <= 8:
        complexity = "low"
    elif word_count <= 18:
        complexity = "medium"
    else:
        complexity = "high"

    multi_concept = (
        required_count is not None
        or intent == "comparison"
        or bool(
            re.search(
                r"\b(and|between|multiple|several|both|all|each)\b",
                query.lower(),
            )
        )
    )

    return {
        "query": query,
        "intent": intent,
        "complexity": complexity,
        "multi_concept": multi_concept,
        "required_count": required_count,
        "learning_context": learning_context,
    }
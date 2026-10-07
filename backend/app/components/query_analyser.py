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
        r"\b(exam|revision|study|prepare|preparation|"
        r"important questions?)\b",
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


def extract_named_requirements(query: str) -> list[str]:
    """
    Extract explicit multi-part requirements from questions.

    This is intentionally conservative in Phase 1.
    We are identifying what the user explicitly asks for,
    not yet trying to infer requirements from the PDF.
    """

    q = query.strip()

    requirements = []

    # Pattern:
    # "A, B, C, D and E"
    #
    # We only use this for phrases following common
    # requirement indicators.

    indicators = [
        "explain",
        "describe",
        "cover",
        "include",
        "discuss",
        "identify",
        "list",
    ]

    for indicator in indicators:

        pattern = rf"\b{indicator}\b(.+?)(?:\.|$)"

        match = re.search(
            pattern,
            q,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        phrase = match.group(1)

        # Split on commas and "and".
        parts = re.split(
            r",|\band\b",
            phrase,
            flags=re.IGNORECASE,
        )

        cleaned_parts = []

        for part in parts:

            part = part.strip(
                " ,:;.-"
            )

            if not part:
                continue

            # Avoid treating generic phrases as evidence
            # requirements.
            generic_phrases = {
                "the complete",
                "the following",
                "the concept",
                "the topic",
                "how",
                "why",
                "the",
            }

            if part.lower() in generic_phrases:
                continue

            cleaned_parts.append(part)

        if len(cleaned_parts) >= 2:
            requirements.extend(cleaned_parts)

        break

    return requirements


def infer_evidence_requirements(
    query: str,
    intent: str,
    learning_context: str,
    required_count,
    multi_concept: bool,
) -> dict:

    named_requirements = extract_named_requirements(
        query
    )

    requirements = []

    # --------------------------------------------------
    # Explicit multi-part requirements
    # --------------------------------------------------

    if named_requirements:
        requirements.extend(
            named_requirements
        )

    # --------------------------------------------------
    # Intent-based requirements
    # --------------------------------------------------

    if intent == "definition":

        requirements.extend(
            [
                "definition",
                "key concept",
            ]
        )

    elif intent == "comparison":

        requirements.extend(
            [
                "first concept",
                "second concept",
                "comparison points",
            ]
        )

    elif intent == "explanation":

        requirements.extend(
            [
                "main concept",
                "supporting explanation",
            ]
        )

    elif intent == "summarization":

        requirements.extend(
            [
                "key points",
                "main ideas",
            ]
        )

    elif intent == "example":

        requirements.extend(
            [
                "concept",
                "examples or applications",
            ]
        )

    elif intent == "general":

        requirements.append(
            "relevant information"
        )

    # --------------------------------------------------
    # Required-count questions
    # --------------------------------------------------

    if required_count is not None:

        requirements.append(
            f"{required_count} requested items"
        )

    # --------------------------------------------------
    # Learning-context requirements
    # --------------------------------------------------

    if learning_context == "exam_preparation":

        requirements.append(
            "important exam-focused information"
        )

    elif learning_context == "assignment":

        requirements.append(
            "assignment-relevant supporting evidence"
        )

    elif learning_context == "research":

        requirements.append(
            "broader supporting evidence"
        )

    # --------------------------------------------------
    # Remove duplicates while preserving order
    # --------------------------------------------------

    unique_requirements = []

    seen = set()

    for requirement in requirements:

        normalized = requirement.lower().strip()

        if normalized in seen:
            continue

        seen.add(normalized)

        unique_requirements.append(
            requirement
        )

    return {
        "requirements": unique_requirements,
        "explicit_requirements": named_requirements,
        "requirement_count": len(
            unique_requirements
        ),
    }


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
            "evidence_requirements": [],
            "explicit_requirements": [],
            "requirement_count": 0,
        }

    intent = detect_intent(query)

    learning_context = detect_learning_context(
        query
    )

    required_count = detect_required_count(
        query
    )

    word_count = len(
        query.split()
    )

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
                r"\b(and|between|multiple|several|"
                r"both|all|each)\b",
                query.lower(),
            )
        )
    )

    evidence_plan = infer_evidence_requirements(
        query=query,
        intent=intent,
        learning_context=learning_context,
        required_count=required_count,
        multi_concept=multi_concept,
    )

    return {
        "query": query,
        "intent": intent,
        "complexity": complexity,
        "multi_concept": multi_concept,
        "required_count": required_count,
        "learning_context": learning_context,

        # New adaptive information
        "evidence_requirements": evidence_plan[
            "requirements"
        ],
        "explicit_requirements": evidence_plan[
            "explicit_requirements"
        ],
        "requirement_count": evidence_plan[
            "requirement_count"
        ],
    }
import time

from google import genai

from backend.app.config import GEMINI_API_KEY


# ==================================================================
# GEMINI CLIENT
# ==================================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

GENERATION_MODEL = "gemini-3.6-flash"

MAX_GENERATION_ATTEMPTS = 3


# ==================================================================
# PERSONALIZATION INSTRUCTIONS
# ==================================================================

def build_personalization_instructions(
    personalization_context: dict | None,
) -> str:
    """
    Convert Phase 7 learner preferences into instructions
    for the generation model.
    """

    if not personalization_context:

        return """
No learner-specific preferences are available.

Use a clear, structured academic explanation suitable
for a university student.
"""

    preferred_detail = (
        personalization_context.get(
            "preferred_detail",
            "medium",
        )
    )

    preferred_format = (
        personalization_context.get(
            "preferred_format",
            "structured",
        )
    )

    preferred_examples = (
        personalization_context.get(
            "preferred_examples",
            True,
        )
    )

    preferred_citations = (
        personalization_context.get(
            "preferred_citations",
            True,
        )
    )

    instructions = f"""
Learner preferred detail level:
{preferred_detail}

Learner preferred response format:
{preferred_format}

Learner prefers examples:
{preferred_examples}

Learner prefers citations:
{preferred_citations}
"""

    # --------------------------------------------------------------
    # Detail preference
    # --------------------------------------------------------------

    if preferred_detail == "high":

        instructions += """
Provide a detailed university-level explanation.
Explain important concepts, relationships, and
contributions clearly.
Avoid unnecessary repetition.
"""

    elif preferred_detail == "low":

        instructions += """
Keep the response concise.
Focus on the essential academic concepts and
avoid unnecessary elaboration.
"""

    else:

        instructions += """
Use a balanced level of detail appropriate for
university-level conceptual learning.
"""

    # --------------------------------------------------------------
    # Format preference
    # --------------------------------------------------------------

    if preferred_format == "structured":

        instructions += """
Use headings, numbered points, or bullet points
when they improve clarity.
"""

    elif preferred_format == "paragraph":

        instructions += """
Prefer connected explanatory paragraphs while
maintaining academic clarity.
"""

    else:

        instructions += """
Use the response structure that best fits
the user's question.
"""

    # --------------------------------------------------------------
    # Example preference
    # --------------------------------------------------------------

    if preferred_examples:

        instructions += """
Include examples only when they are directly
supported by the supplied academic evidence.
Never invent an unsupported example.
"""

    else:

        instructions += """
Do not add examples unless the user's question
explicitly requires them.
"""

    # --------------------------------------------------------------
    # Citation preference
    # --------------------------------------------------------------

    if preferred_citations:

        instructions += """
Use source citations for major factual claims.
"""

    else:

        instructions += """
Citations are still required when needed for
academic grounding, even if the learner prefers
fewer citations.
"""

    return instructions


# ==================================================================
# EVIDENCE BLOCK BUILDER
# ==================================================================

def build_evidence_blocks(
    evidence: list,
) -> str:
    """
    Convert Phase 5 evidence into structured context
    for the generation model.
    """

    if not evidence:

        return (
            "No academic evidence was supplied."
        )

    evidence_blocks = []

    for index, document in enumerate(
        evidence,
        start=1,
    ):

        source = document.meta.get(
            "source",
            "Unknown source",
        )

        page = document.meta.get(
            "page_number",
            "Unknown page",
        )

        evidence_score = document.meta.get(
            "evidence_score",
            document.score
            if document.score is not None
            else 0.0,
        )

        content = (
            document.content.strip()
            if document.content
            else ""
        )

        evidence_blocks.append(
            f"""
[EVIDENCE {index}]

Source: {source}
Page: {page}
Evidence Score: {evidence_score:.4f}

Academic Content:
{content}
"""
        )

    return "\n".join(
        evidence_blocks
    )


# ==================================================================
# GENERATION PROMPT
# ==================================================================

def build_generation_prompt(
    query: str,
    evidence: list,
    query_context: dict,
    personalization_context: dict | None = None,
) -> str:
    """
    Build the final grounded academic generation prompt.

    Phase 5 provides the evidence.
    Phase 7 provides learner preferences.
    """

    intent = query_context.get(
        "intent",
        "general",
    )

    learning_context = query_context.get(
        "learning_context",
        "conceptual_learning",
    )

    complexity = query_context.get(
        "complexity",
        "medium",
    )

    required_count = query_context.get(
        "required_count",
        None,
    )

    discovered_items = query_context.get(
        "discovered_items",
        [],
    )

    validation = query_context.get(
        "validation",
        {},
    )

    personalization_instructions = (
        build_personalization_instructions(
            personalization_context
        )
    )

    evidence_text = build_evidence_blocks(
        evidence
    )

    # --------------------------------------------------------------
    # Discovered educational items
    # --------------------------------------------------------------

    if discovered_items:

        discovered_items_text = "\n".join(
            f"- {item}"
            for item in discovered_items
        )

    else:

        discovered_items_text = (
            "No specific multi-item structure was detected."
        )

    # --------------------------------------------------------------
    # Validation information
    # --------------------------------------------------------------

    coverage = validation.get(
        "coverage",
        validation.get(
            "coverage_score",
            "unknown",
        ),
    )

    prompt = f"""
You are an academic learning assistant.

Your task is to answer the user's question using
ONLY the academic evidence supplied in this prompt.

The evidence comes from an academic retrieval system
and has already been selected and re-ranked for
relevance to the question.

============================================================
USER QUESTION
============================================================

{query}

============================================================
EDUCATIONAL CONTEXT
============================================================

Learning context:
{learning_context}

Question intent:
{intent}

Question complexity:
{complexity}

Required item count:
{required_count}

============================================================
DISCOVERED EDUCATIONAL ITEMS
============================================================

{discovered_items_text}

============================================================
EVIDENCE COVERAGE
============================================================

{coverage}

============================================================
LEARNER PERSONALIZATION
============================================================

{personalization_instructions}

============================================================
STRICT ACADEMIC GROUNDING RULES
============================================================

1. Use ONLY the supplied academic evidence.

2. Do not invent facts.

3. Do not invent definitions.

4. Do not invent explanations.

5. Do not invent examples.

6. Do not introduce outside academic knowledge.

7. Do not make claims that cannot be supported
   by the supplied evidence.

8. Answer the user's actual question directly.

9. If the user requests multiple items, explain
   each requested item separately.

10. Preserve important terminology from the
    supplied academic material.

11. If the evidence is insufficient for a particular
    part of the question, explicitly state that the
    supplied evidence is insufficient for that part.

12. Do not pretend that unsupported information
    exists in the academic sources.

============================================================
ANSWER STRUCTURE
============================================================

Use a structure appropriate to the user's question.

For questions requesting multiple concepts:

1. Name the concept.
2. Explain what it is.
3. Explain why it matters when supported.
4. Explain its contribution when supported.

Do not force this structure if the supplied evidence
does not support all four aspects.

============================================================
ACADEMIC CITATIONS
============================================================

For major factual claims, use:

[Source: filename, p. X]

If multiple pages from the same source support a claim,
you may use:

[Source: filename, pp. X-Y]

Use the actual source filename and page number supplied
with the evidence.

Do not invent page numbers.

Do not invent source names.

============================================================
INTERNAL SYSTEM INFORMATION
============================================================

Do NOT mention:

- retrieval
- vector databases
- embeddings
- reranking
- evidence scores
- validation
- adaptive retrieval
- learner profile implementation
- personalization implementation
- internal pipeline stages

The user should receive a normal academic answer,
not a description of the internal RAG system.

============================================================
ACADEMIC EVIDENCE
============================================================

{evidence_text}

============================================================
FINAL TASK
============================================================

Answer the user's question now.

The answer must be:

- academically grounded
- clear
- directly relevant
- appropriately structured
- personalized in presentation
- supported by the supplied evidence
- properly cited
"""

    return prompt


# ==================================================================
# TEMPORARY ERROR DETECTION
# ==================================================================

def is_temporary_generation_error(
    error: Exception,
) -> bool:
    """
    Detect temporary Gemini service failures that may
    succeed after retrying.
    """

    error_message = str(
        error
    ).lower()

    temporary_patterns = [
        "503",
        "unavailable",
        "high demand",
        "temporarily unavailable",
        "service unavailable",
    ]

    return any(
        pattern in error_message
        for pattern in temporary_patterns
    )


# ==================================================================
# GENERATE RESPONSE
# ==================================================================

def generate_response(
    query: str,
    evidence: list,
    query_context: dict,
    personalization_context: dict | None = None,
) -> str:
    """
    Generate the final academic response.

    Includes retry handling for temporary Gemini
    service failures.
    """

    # --------------------------------------------------------------
    # Validate query
    # --------------------------------------------------------------

    if not query or not query.strip():

        return (
            "Please provide a question."
        )

    # --------------------------------------------------------------
    # Validate evidence
    # --------------------------------------------------------------

    if not evidence:

        return (
            "I could not find sufficient academic "
            "evidence to answer this question."
        )

    # --------------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------------

    prompt = build_generation_prompt(
        query=query,
        evidence=evidence,
        query_context=query_context,
        personalization_context=(
            personalization_context
        ),
    )

    # --------------------------------------------------------------
    # Generation with retry
    # --------------------------------------------------------------

    for attempt in range(
        1,
        MAX_GENERATION_ATTEMPTS + 1,
    ):

        try:

            response = (
                client.models.generate_content(
                    model=GENERATION_MODEL,
                    contents=prompt,
                )
            )

            # ------------------------------------------------------
            # Validate response
            # ------------------------------------------------------

            if (
                not response
                or not response.text
                or not response.text.strip()
            ):

                return (
                    "The generation model did not "
                    "return a response."
                )

            return response.text.strip()

        except Exception as error:

            # ------------------------------------------------------
            # Temporary Gemini service error
            # ------------------------------------------------------

            if is_temporary_generation_error(
                error
            ):

                if (
                    attempt
                    < MAX_GENERATION_ATTEMPTS
                ):

                    wait_seconds = (
                        attempt * 2
                    )

                    print(
                        "\nGemini generation "
                        "temporarily unavailable."
                    )

                    print(
                        f"Retrying in "
                        f"{wait_seconds} seconds..."
                    )

                    time.sleep(
                        wait_seconds
                    )

                    continue

                # --------------------------------------------------
                # All retry attempts exhausted
                # --------------------------------------------------

                return (
                    "The academic evidence was successfully "
                    "retrieved, composed, validated, and "
                    "re-ranked, but the Gemini generation "
                    "service is temporarily unavailable. "
                    "Please try again shortly."
                )

            # ------------------------------------------------------
            # Non-temporary error
            # ------------------------------------------------------

            return (
                "The academic evidence pipeline "
                "completed successfully, but response "
                "generation failed.\n\n"
                f"Generation error: {error}"
            )

    # --------------------------------------------------------------
    # Safety fallback
    # --------------------------------------------------------------

    return (
        "Response generation was unsuccessful."
    )
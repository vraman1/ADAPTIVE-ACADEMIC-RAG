import sys
from pathlib import Path

# ==============================================================
# PROJECT PATH
# ==============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ==============================================================
# IMPORTS
# ==============================================================

import streamlit as st

from backend.app.pipelines.adaptive_rag_pipeline import (
    adaptive_retrieve,
)

from backend.app.components.user_profile import (
    create_default_profile,
    record_feedback,
    analyze_feedback,
    update_preferences,
)


# ==============================================================
# PAGE CONFIGURATION
# ==============================================================

st.set_page_config(
    page_title="Adaptive Academic RAG",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================
# CONSTANTS
# ==============================================================

RAW_DOCUMENTS_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw_documents"
)


# ==============================================================
# SESSION STATE
# ==============================================================

if "user_profile" not in st.session_state:
    st.session_state.user_profile = (
        create_default_profile()
    )

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "last_query" not in st.session_state:
    st.session_state.last_query = ""

if "last_source" not in st.session_state:
    st.session_state.last_source = None

if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False


# ==============================================================
# HELPER FUNCTIONS
# ==============================================================

def get_pdf_files() -> list[Path]:
    """
    Read all PDF files directly from data/raw_documents.

    No PDF filenames are hard-coded.
    """

    if not RAW_DOCUMENTS_DIR.exists():
        return []

    return sorted(
        RAW_DOCUMENTS_DIR.glob("*.pdf"),
        key=lambda path: path.name.lower(),
    )


def get_generation_response(result: dict) -> str:
    """
    Safely extract the generated academic response.
    """

    generation = result.get(
        "generation",
        {},
    )

    if not generation:
        return "No generated response was returned."

    return generation.get(
        "response",
        "No generated response was returned.",
    )


def reset_profile():
    """
    Reset learner profile to the default profile.
    """

    st.session_state.user_profile = (
        create_default_profile()
    )

    st.session_state.feedback_given = False


def format_coverage(value) -> str:
    """
    Format evidence coverage safely.
    """

    if isinstance(value, (int, float)):
        return f"{value:.3f}"

    return str(value)


# ==============================================================
# LOAD PDF FILES
# ==============================================================

pdf_files = get_pdf_files()


# ==============================================================
# SIDEBAR
# ==============================================================

with st.sidebar:

    # ----------------------------------------------------------
    # ACADEMIC SOURCE
    # ----------------------------------------------------------

    st.markdown("## 📚 Academic Source")

    source_options = [
        "All Academic PDFs"
    ] + [
        pdf.name
        for pdf in pdf_files
    ]

    selected_source_label = st.selectbox(
        "Select the PDF to search",
        source_options,
        index=0,
        help=(
            "PDF files are read automatically from "
            "data/raw_documents."
        ),
    )

    # ----------------------------------------------------------
    # CONVERT UI SELECTION TO RETRIEVAL SOURCE
    # ----------------------------------------------------------

    if selected_source_label == "All Academic PDFs":

        selected_source = None

    else:

        selected_source = selected_source_label

    # ----------------------------------------------------------
    # SOURCE INFORMATION
    # ----------------------------------------------------------

    if selected_source is None:

        st.info(
            "Searching across all indexed academic PDFs."
        )

    else:

        st.info(
            f"Searching only:\n\n"
            f"**{selected_source}**"
        )

    st.caption(
        f"{len(pdf_files)} PDF(s) found in "
        "`data/raw_documents`."
    )

    # ----------------------------------------------------------
    # REFRESH PDF LIST
    # ----------------------------------------------------------

    if st.button(
        "🔄 Refresh PDF List",
        use_container_width=True,
    ):

        st.rerun()

    st.divider()

    # ==========================================================
    # LEARNER PROFILE
    # ==========================================================

    st.markdown("## 🎓 Learner Profile")

    st.caption(
        "These preferences affect how the generated "
        "academic answer is presented."
    )

    profile = st.session_state.user_profile

    preferences = profile[
        "learning_preferences"
    ]

    # ----------------------------------------------------------
    # DETAIL LEVEL
    # ----------------------------------------------------------

    detail_options = [
        "low",
        "medium",
        "high",
    ]

    current_detail = preferences.get(
        "preferred_detail",
        "medium",
    )

    selected_detail = st.selectbox(
        "Preferred detail level",
        detail_options,
        index=detail_options.index(
            current_detail
        ),
    )

    preferences[
        "preferred_detail"
    ] = selected_detail

    # ----------------------------------------------------------
    # FORMAT
    # ----------------------------------------------------------

    format_options = [
        "structured",
        "paragraph",
    ]

    current_format = preferences.get(
        "preferred_format",
        "structured",
    )

    selected_format = st.selectbox(
        "Preferred response format",
        format_options,
        index=format_options.index(
            current_format
        ),
    )

    preferences[
        "preferred_format"
    ] = selected_format

    # ----------------------------------------------------------
    # EXAMPLES
    # ----------------------------------------------------------

    preferences[
        "preferred_examples"
    ] = st.checkbox(
        "Include examples when supported",
        value=preferences.get(
            "preferred_examples",
            True,
        ),
    )

    # ----------------------------------------------------------
    # CITATIONS
    # ----------------------------------------------------------

    preferences[
        "preferred_citations"
    ] = st.checkbox(
        "Show academic citations",
        value=preferences.get(
            "preferred_citations",
            True,
        ),
    )

    st.divider()

    # ==========================================================
    # PROFILE STATISTICS
    # ==========================================================

    st.markdown("### Profile Statistics")

    st.write(
        f"**Interactions:** "
        f"{profile.get('interaction_count', 0)}"
    )

    feedback_analysis = analyze_feedback(
        profile
    )

    st.write(
        f"**Feedback:** "
        f"{feedback_analysis['total_feedback']}"
    )

    st.write(
        f"**Positive:** "
        f"{feedback_analysis['positive_feedback']}"
    )

    st.write(
        f"**Negative:** "
        f"{feedback_analysis['negative_feedback']}"
    )

    st.write(
        f"**Satisfaction:** "
        f"{feedback_analysis['satisfaction_ratio']}"
    )

    st.divider()

    # ==========================================================
    # RESET PROFILE
    # ==========================================================

    if st.button(
        "Reset Learner Profile",
        use_container_width=True,
    ):

        reset_profile()

        st.rerun()


# ==============================================================
# MAIN HEADER
# ==============================================================

st.title(
    "🎓 Adaptive Academic RAG"
)

st.subheader(
    "Adaptive Retrieval-Augmented Generation "
    "for Intelligent Academic Knowledge Management"
)

st.caption(
    "Retrieve → Compose → Validate → "
    "Targeted Re-retrieve → Re-compose → "
    "Re-rank → Generate"
)


# ==============================================================
# SOURCE STATUS
# ==============================================================

if selected_source is None:

    st.success(
        "📚 Source: **All Academic PDFs**"
    )

else:

    st.success(
        f"📄 Source: **{selected_source}**"
    )


# ==============================================================
# NO PDF WARNING
# ==============================================================

if not pdf_files:

    st.error(
        "No PDF files were found in "
        "`data/raw_documents`."
    )

    st.info(
        "Place your academic PDF files inside:\n\n"
        f"`{RAW_DOCUMENTS_DIR}`"
    )


# ==============================================================
# QUERY INPUT
# ==============================================================

st.markdown(
    "### Ask an Academic Question"
)

query = st.text_area(
    "Academic question",
    height=130,
    placeholder=(
        "Enter your academic question here..."
    ),
    label_visibility="collapsed",
)


# ==============================================================
# GENERATE BUTTON
# ==============================================================

generate_button = st.button(
    "🔍 Generate Academic Answer",
    type="primary",
    use_container_width=True,
)


# ==============================================================
# RUN ADAPTIVE RAG
# ==============================================================

if generate_button:

    # ----------------------------------------------------------
    # EMPTY QUERY
    # ----------------------------------------------------------

    if not query.strip():

        st.warning(
            "Please enter an academic question."
        )

    # ----------------------------------------------------------
    # NO PDF
    # ----------------------------------------------------------

    elif not pdf_files:

        st.error(
            "No academic PDFs are available in "
            "`data/raw_documents`."
        )

    # ----------------------------------------------------------
    # RUN PIPELINE
    # ----------------------------------------------------------

    else:

        st.session_state.last_query = (
            query.strip()
        )

        st.session_state.last_source = (
            selected_source
        )

        st.session_state.feedback_given = (
            False
        )

        with st.spinner(
            "Analyzing the question, retrieving "
            "academic evidence, validating it, "
            "and generating the answer..."
        ):

            try:

                result = adaptive_retrieve(
                    query=query.strip(),

                    # --------------------------------------------------
                    # SELECTED PDF
                    # --------------------------------------------------

                    source=selected_source,

                    # --------------------------------------------------
                    # RETRIEVAL SETTINGS
                    # --------------------------------------------------

                    initial_top_k=3,
                    adaptive_top_k=8,
                    max_iterations=3,

                    # --------------------------------------------------
                    # LEARNER PROFILE
                    # --------------------------------------------------

                    user_profile=(
                        st.session_state.user_profile
                    ),
                )

                st.session_state.last_result = (
                    result
                )

            except Exception as error:

                st.error(
                    "The Adaptive Academic RAG pipeline "
                    "encountered an error."
                )

                st.exception(
                    error
                )


# ==============================================================
# GET LAST RESULT
# ==============================================================

result = st.session_state.last_result


# ==============================================================
# DISPLAY RESULT
# ==============================================================

if result is not None:

    # ==========================================================
    # ADAPTIVE PIPELINE STATUS
    # ==========================================================

    st.markdown(
        "### 🔄 Adaptive Pipeline Status"
    )

    col1, col2, col3, col4 = st.columns(4)

    # ----------------------------------------------------------
    # ADAPTIVE STATUS
    # ----------------------------------------------------------

    with col1:

        st.metric(
            "Adaptive Retrieval",
            result.get(
                "adaptive_status",
                "Unknown",
            ),
        )

    # ----------------------------------------------------------
    # ITERATIONS
    # ----------------------------------------------------------

    with col2:

        st.metric(
            "Iterations",
            result.get(
                "iterations",
                0,
            ),
        )

    # ----------------------------------------------------------
    # EVIDENCE COUNT
    # ----------------------------------------------------------

    with col3:

        evidence = result.get(
            "final_evidence",
            result.get(
                "evidence",
                [],
            ),
        )

        st.metric(
            "Evidence Count",
            len(evidence),
        )

    # ----------------------------------------------------------
    # COVERAGE
    # ----------------------------------------------------------

    with col4:

        validation = result.get(
            "validation",
            {},
        )

        coverage = validation.get(
            "coverage",
            validation.get(
                "coverage_score",
                0.0,
            ),
        )

        st.metric(
            "Evidence Coverage",
            format_coverage(
                coverage
            ),
        )


    # ==========================================================
    # QUERY ANALYSIS
    # ==========================================================

    with st.expander(
        "🧠 Educational Query Analysis",
        expanded=False,
    ):

        query_context = result.get(
            "query_context",
            {},
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                "**Intent:**",
                query_context.get(
                    "intent",
                    "Unknown",
                ),
            )

            st.write(
                "**Learning Context:**",
                query_context.get(
                    "learning_context",
                    "Unknown",
                ),
            )

            st.write(
                "**Complexity:**",
                query_context.get(
                    "complexity",
                    "Unknown",
                ),
            )

        with col2:

            st.write(
                "**Required Count:**",
                query_context.get(
                    "required_count",
                    "Not specified",
                ),
            )

            st.write(
                "**Evidence Requirements:**"
            )

            evidence_requirements = (
                query_context.get(
                    "evidence_requirements",
                    [],
                )
            )

            if evidence_requirements:

                for requirement in (
                    evidence_requirements
                ):

                    st.write(
                        f"- {requirement}"
                    )

            else:

                st.write(
                    "No explicit evidence requirements."
                )

            st.write(
                "**Discovered Items:**"
            )

            discovered_items = (
                query_context.get(
                    "discovered_items",
                    [],
                )
            )

            if discovered_items:

                for item in discovered_items:

                    st.write(
                        f"- {item}"
                    )

            else:

                st.write(
                    "No multi-item structure detected."
                )


    # ==========================================================
    # PERSONALIZATION
    # ==========================================================

    with st.expander(
        "👤 Learner Personalization",
        expanded=False,
    ):

        personalization = result.get(
            "personalization",
            {},
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                "**Preferred Detail:**",
                personalization.get(
                    "preferred_detail",
                    "medium",
                ),
            )

            st.write(
                "**Preferred Format:**",
                personalization.get(
                    "preferred_format",
                    "structured",
                ),
            )

        with col2:

            st.write(
                "**Examples:**",
                "Yes"
                if personalization.get(
                    "preferred_examples",
                    True,
                )
                else "No",
            )

            st.write(
                "**Citations:**",
                "Yes"
                if personalization.get(
                    "preferred_citations",
                    True,
                )
                else "No",
            )


    # ==========================================================
    # VALIDATION
    # ==========================================================

    with st.expander(
        "✅ Evidence Validation",
        expanded=False,
    ):

        validation = result.get(
            "validation",
            {},
        )

        sufficient = validation.get(
            "sufficient",
            False,
        )

        if sufficient:

            st.success(
                "Evidence was considered sufficient."
            )

        else:

            st.warning(
                "Evidence was not fully sufficient."
            )

        st.write(
            "**Coverage:**",
            format_coverage(
                validation.get(
                    "coverage",
                    validation.get(
                        "coverage_score",
                        0.0,
                    ),
                )
            ),
        )

        missing_requirements = (
            validation.get(
                "missing_requirements",
                [],
            )
        )

        if missing_requirements:

            st.write(
                "**Missing Requirements:**"
            )

            for requirement in (
                missing_requirements
            ):

                st.write(
                    f"- {requirement}"
                )

        else:

            st.write(
                "**Missing Requirements:** None"
            )


    # ==========================================================
    # FINAL ACADEMIC ANSWER
    # ==========================================================

    st.markdown(
        "### 📚 Academic Answer"
    )

    response = get_generation_response(
        result
    )

    st.markdown(
        response
    )


    # ==========================================================
    # FEEDBACK
    # ==========================================================

    st.markdown(
        "### Was this answer useful?"
    )

    feedback_col1, feedback_col2, feedback_col3 = (
        st.columns(
            [1, 1, 5]
        )
    )

    with feedback_col1:

        positive_feedback = st.button(
            "👍 Helpful",
            use_container_width=True,
            disabled=(
                st.session_state.feedback_given
            ),
        )

    with feedback_col2:

        negative_feedback = st.button(
            "👎 Not Helpful",
            use_container_width=True,
            disabled=(
                st.session_state.feedback_given
            ),
        )

    if (
        positive_feedback
        or negative_feedback
    ):

        rating = (
            "positive"
            if positive_feedback
            else "negative"
        )

        updated_profile = record_feedback(
            profile=(
                st.session_state.user_profile
            ),
            query=(
                st.session_state.last_query
            ),
            rating=rating,
        )

        feedback_analysis = (
            analyze_feedback(
                updated_profile
            )
        )

        updated_profile = (
            update_preferences(
                profile=updated_profile,
                feedback_analysis=(
                    feedback_analysis
                ),
            )
        )

        st.session_state.user_profile = (
            updated_profile
        )

        st.session_state.feedback_given = (
            True
        )

        if rating == "positive":

            st.success(
                "Thanks! Your positive feedback "
                "has been added to the learner profile."
            )

        else:

            st.info(
                "Thanks! Your feedback has been "
                "recorded for future personalization."
            )

    elif st.session_state.feedback_given:

        st.caption(
            "Feedback has already been recorded "
            "for this answer."
        )


    # ==========================================================
    # ACADEMIC SOURCES
    # ==============================================================

    st.markdown(
        "### 📖 Academic Sources"
    )

    generation = result.get(
        "generation",
        {},
    )

    generation_sources = generation.get(
        "sources",
        [],
    )

    if generation_sources:

        displayed_sources = set()

        for source in generation_sources:

            source_name = source.get(
                "source",
                "Unknown source",
            )

            page = source.get(
                "page",
                "Unknown",
            )

            source_key = (
                source_name,
                page,
            )

            if source_key in displayed_sources:
                continue

            displayed_sources.add(
                source_key
            )

            st.write(
                f"📄 **{source_name}** "
                f"— Page {page}"
            )

    else:

        st.info(
            "No source information was returned."
        )


    # ==========================================================
    # EVIDENCE USED
    # ==========================================================

    with st.expander(
        "🔎 View Evidence Used",
        expanded=False,
    ):

        final_evidence = result.get(
            "final_evidence",
            result.get(
                "evidence",
                [],
            ),
        )

        if final_evidence:

            for index, document in enumerate(
                final_evidence,
                start=1,
            ):

                source = document.meta.get(
                    "source",
                    "Unknown",
                )

                page = document.meta.get(
                    "page_number",
                    "Unknown",
                )

                evidence_score = (
                    document.meta.get(
                        "evidence_score",
                        document.score,
                    )
                )

                st.markdown(
                    f"#### Evidence {index}"
                )

                st.write(
                    f"**Source:** {source}"
                )

                st.write(
                    f"**Page:** {page}"
                )

                if evidence_score is not None:

                    st.write(
                        f"**Evidence score:** "
                        f"{evidence_score:.4f}"
                    )

                with st.container(
                    border=True
                ):

                    st.write(
                        document.content
                    )

                if index < len(
                    final_evidence
                ):

                    st.divider()

        else:

            st.info(
                "No evidence was returned."
            )


    # ==========================================================
    # ADAPTIVE RETRIEVAL HISTORY
    # ==========================================================

    with st.expander(
        "🔄 Adaptive Retrieval History",
        expanded=False,
    ):

        history = result.get(
            "retrieval_history",
            [],
        )

        if history:

            for position, iteration in enumerate(
                history
            ):

                st.markdown(
                    f"#### Iteration "
                    f"{iteration.get('iteration')}"
                )

                st.write(
                    "**Stage:**",
                    iteration.get(
                        "stage",
                        "Unknown",
                    ),
                )

                queries = iteration.get(
                    "queries",
                    [],
                )

                if queries:

                    st.write(
                        "**Retrieval Queries:**"
                    )

                    for retrieval_query in queries:

                        st.code(
                            retrieval_query
                        )

                candidate_count = iteration.get(
                    "candidate_count",
                    iteration.get(
                        "total_candidate_count",
                        0,
                    ),
                )

                st.write(
                    "**Candidate Count:**",
                    candidate_count,
                )

                st.write(
                    "**Evidence Count:**",
                    iteration.get(
                        "evidence_count",
                        0,
                    ),
                )

                iteration_validation = (
                    iteration.get(
                        "validation",
                        {},
                    )
                )

                st.write(
                    "**Sufficient:**",
                    iteration_validation.get(
                        "sufficient",
                        False,
                    ),
                )

                st.write(
                    "**Coverage:**",
                    format_coverage(
                        iteration_validation.get(
                            "coverage",
                            iteration_validation.get(
                                "coverage_score",
                                0.0,
                            ),
                        )
                    ),
                )

                if position < len(history) - 1:

                    st.divider()


# ==============================================================
# EMPTY STATE
# ==============================================================

else:

    st.info(
        "Select an academic PDF, enter an academic "
        "question, and click Generate Academic Answer."
    )

    if pdf_files:

        st.markdown(
            "### Available Academic PDFs"
        )

        for pdf in pdf_files:

            st.write(
                f"📄 {pdf.name}"
            )

    else:

        st.warning(
            "No PDF files are currently present in "
            "`data/raw_documents`."
        )
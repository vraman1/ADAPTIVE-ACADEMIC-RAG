import streamlit as st

from backend.app.pipelines.adaptive_rag_pipeline import (
    adaptive_retrieve,
)

from backend.app.components.gemini_generator import (
    generate_answer,
)


st.set_page_config(
    page_title="Adaptive Academic RAG",
    page_icon="📚",
    layout="wide",
)


st.title(
    "📚 Adaptive Academic RAG"
)

st.caption(
    "An Adaptive Retrieval-Augmented Generation Framework "
    "for Intelligent Academic Knowledge Management"
)


query = st.text_area(
    "Enter your academic question:",
    placeholder=(
        "Example: Explain the five tiers "
        "of Streaming Analytics Architecture."
    ),
)


if st.button(
    "Ask",
    type="primary",
):

    if not query.strip():

        st.warning(
            "Please enter a question."
        )

    else:

        with st.spinner(
            "Retrieving and validating academic evidence..."
        ):

            result = adaptive_retrieve(
                query=query
            )

        with st.spinner(
            "Generating answer..."
        ):

            answer = generate_answer(
                query=query,
                evidence=result[
                    "evidence"
                ],
                query_context=result[
                    "query_context"
                ],
            )

        st.subheader(
            "Answer"
        )

        st.write(
            answer
        )

        st.divider()

        st.subheader(
            "Adaptive RAG Details"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Iterations",
                result[
                    "iterations"
                ],
            )

        with col2:

            st.metric(
                "Adaptive Retrieval",
                "Yes"
                if result[
                    "adaptive_retrieval"
                ]
                else "No",
            )

        with col3:

            st.metric(
                "Evidence Items",
                len(
                    result[
                        "evidence"
                    ]
                ),
            )

        st.subheader(
            "Query Analysis"
        )

        st.json(
            result[
                "query_context"
            ]
        )

        st.subheader(
            "Evidence Validation"
        )

        st.json(
            result[
                "validation"
            ]
        )

        st.subheader(
            "Retrieved Evidence"
        )

        for index, document in enumerate(
            result["evidence"],
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

            score = document.score

            with st.expander(
                f"Evidence {index} — "
                f"{source}, Page {page}"
            ):

                st.write(
                    f"**Retrieval score:** {score}"
                )

                st.write(
                    document.content
                )

        st.subheader(
            "Adaptive Retrieval History"
        )

        for history in result[
            "retrieval_history"
        ]:

            with st.expander(
                f"Iteration "
                f"{history['iteration']} — "
                f"{history['stage']}"
            ):

                st.write(
                    "Queries:"
                )

                for q in history[
                    "queries"
                ]:

                    st.write(
                        f"- {q}"
                    )

                st.write(
                    "Validation:"
                )

                st.json(
                    history[
                        "validation"
                    ]
                )
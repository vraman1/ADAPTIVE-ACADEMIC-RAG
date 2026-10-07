from backend.app.components.user_profile import (
    create_default_profile,
    record_interaction,
    record_feedback,
    analyze_feedback,
    update_preferences,
    build_personalization_context,
)


def main():

    # ===============================================================
    # PHASE 7 — USER PROFILE & FEEDBACK
    # ===============================================================

    print("\n" + "=" * 70)
    print("PHASE 7 — USER PROFILE & FEEDBACK")
    print("=" * 70)

    # ---------------------------------------------------------------
    # Create learner profile
    # ---------------------------------------------------------------

    profile = create_default_profile()

    print("\nDEFAULT PROFILE")
    print(profile)

    # ---------------------------------------------------------------
    # Simulate interaction
    # ---------------------------------------------------------------

    query_context = {
        "intent": "explanation",
        "learning_context": "conceptual_learning",
        "complexity": "high",
    }

    response = (
        "Customer Lifetime Value is maximised through "
        "five building blocks."
    )

    profile = record_interaction(
        profile=profile,
        query=(
            "Explain the five building blocks "
            "that maximise CLV."
        ),
        query_context=query_context,
        response=response,
    )

    # ---------------------------------------------------------------
    # Record learner feedback
    # ---------------------------------------------------------------

    profile = record_feedback(
        profile=profile,
        query=(
            "Explain the five building blocks "
            "that maximise CLV."
        ),
        rating="positive",
        comment="The structured explanation was useful.",
    )

    # ---------------------------------------------------------------
    # Analyze feedback
    # ---------------------------------------------------------------

    feedback_analysis = analyze_feedback(
        profile
    )

    # ---------------------------------------------------------------
    # Adapt preferences
    # ---------------------------------------------------------------

    profile = update_preferences(
        profile=profile,
        feedback_analysis=feedback_analysis,
    )

    # ---------------------------------------------------------------
    # Build personalization context
    # ---------------------------------------------------------------

    personalization_context = (
        build_personalization_context(
            profile
        )
    )

    # ---------------------------------------------------------------
    # Display results
    # ---------------------------------------------------------------

    print("\nLEARNING HISTORY")
    print(
        f"Interactions: "
        f"{profile['interaction_count']}"
    )

    print("\nFEEDBACK ANALYSIS")

    print(
        f"Total feedback: "
        f"{feedback_analysis['total_feedback']}"
    )

    print(
        f"Positive feedback: "
        f"{feedback_analysis['positive_feedback']}"
    )

    print(
        f"Negative feedback: "
        f"{feedback_analysis['negative_feedback']}"
    )

    print(
        f"Satisfaction ratio: "
        f"{feedback_analysis['satisfaction_ratio']}"
    )

    print("\nPERSONALIZATION CONTEXT")

    for key, value in personalization_context.items():
        print(
            f"{key}: {value}"
        )


if __name__ == "__main__":
    main()
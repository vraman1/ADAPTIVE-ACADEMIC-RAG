from datetime import datetime


# -------------------------------------------------------------------
# Default user profile
# -------------------------------------------------------------------

def create_default_profile() -> dict:
    """
    Create a default learner profile.
    """

    return {
        "learning_preferences": {
            "preferred_detail": "medium",
            "preferred_format": "structured",
            "preferred_examples": True,
            "preferred_citations": True,
        },

        "learning_history": [],

        "feedback_history": [],

        "interaction_count": 0,

        "last_updated": None,
    }


# -------------------------------------------------------------------
# Profile validation
# -------------------------------------------------------------------

def ensure_profile(profile: dict | None) -> dict:
    """
    Ensure that a valid profile structure exists.
    """

    if not profile:
        return create_default_profile()

    default_profile = create_default_profile()

    for key, value in default_profile.items():

        if key not in profile:
            profile[key] = value

    for key, value in default_profile[
        "learning_preferences"
    ].items():

        profile[
            "learning_preferences"
        ].setdefault(
            key,
            value,
        )

    return profile


# -------------------------------------------------------------------
# Record interaction
# -------------------------------------------------------------------

def record_interaction(
    profile: dict,
    query: str,
    query_context: dict,
    response: str,
) -> dict:
    """
    Record a learner interaction.
    """

    profile = ensure_profile(profile)

    interaction = {
        "timestamp": datetime.now().isoformat(),

        "query": query,

        "intent": query_context.get(
            "intent",
            "general",
        ),

        "learning_context": query_context.get(
            "learning_context",
            "conceptual_learning",
        ),

        "complexity": query_context.get(
            "complexity",
            "medium",
        ),

        "response": response,
    }

    profile[
        "learning_history"
    ].append(interaction)

    profile[
        "interaction_count"
    ] += 1

    profile[
        "last_updated"
    ] = datetime.now().isoformat()

    return profile


# -------------------------------------------------------------------
# Record feedback
# -------------------------------------------------------------------

def record_feedback(
    profile: dict,
    query: str,
    rating: str,
    comment: str = "",
) -> dict:
    """
    Record learner feedback.

    rating should normally be:
        positive
        negative
    """

    profile = ensure_profile(profile)

    feedback = {
        "timestamp": datetime.now().isoformat(),

        "query": query,

        "rating": rating,

        "comment": comment,
    }

    profile[
        "feedback_history"
    ].append(feedback)

    profile[
        "last_updated"
    ] = datetime.now().isoformat()

    return profile


# -------------------------------------------------------------------
# Analyze feedback
# -------------------------------------------------------------------

def analyze_feedback(
    profile: dict,
) -> dict:
    """
    Analyze accumulated learner feedback.
    """

    profile = ensure_profile(profile)

    feedback_history = profile.get(
        "feedback_history",
        [],
    )

    positive = sum(
        1
        for item in feedback_history
        if item.get("rating") == "positive"
    )

    negative = sum(
        1
        for item in feedback_history
        if item.get("rating") == "negative"
    )

    total = positive + negative

    if total == 0:
        satisfaction = 0.0
    else:
        satisfaction = positive / total

    return {
        "total_feedback": total,
        "positive_feedback": positive,
        "negative_feedback": negative,
        "satisfaction_ratio": round(
            satisfaction,
            3,
        ),
    }


# -------------------------------------------------------------------
# Update learning preferences
# -------------------------------------------------------------------

def update_preferences(
    profile: dict,
    feedback_analysis: dict,
) -> dict:
    """
    Adapt learner preferences using accumulated feedback.

    This is intentionally lightweight so that the profile
    remains interpretable.
    """

    profile = ensure_profile(profile)

    satisfaction = feedback_analysis.get(
        "satisfaction_ratio",
        0.0,
    )

    negative_feedback = feedback_analysis.get(
        "negative_feedback",
        0,
    )

    preferences = profile[
        "learning_preferences"
    ]

    # If the learner has repeatedly provided negative
    # feedback, prefer more structured and detailed answers.
    if negative_feedback >= 2:

        preferences[
            "preferred_detail"
        ] = "high"

        preferences[
            "preferred_format"
        ] = "structured"

        preferences[
            "preferred_citations"
        ] = True

    # Strong positive feedback keeps the current
    # personalization settings.
    elif satisfaction >= 0.75:

        preferences.setdefault(
            "preferred_detail",
            "medium",
        )

        preferences.setdefault(
            "preferred_format",
            "structured",
        )

    profile[
        "last_updated"
    ] = datetime.now().isoformat()

    return profile


# -------------------------------------------------------------------
# Build personalization context
# -------------------------------------------------------------------

def build_personalization_context(
    profile: dict,
) -> dict:
    """
    Convert the learner profile into a compact context
    that can be passed to the generation stage.
    """

    profile = ensure_profile(profile)

    preferences = profile[
        "learning_preferences"
    ]

    feedback_analysis = analyze_feedback(
        profile
    )

    return {
        "preferred_detail": preferences.get(
            "preferred_detail",
            "medium",
        ),

        "preferred_format": preferences.get(
            "preferred_format",
            "structured",
        ),

        "preferred_examples": preferences.get(
            "preferred_examples",
            True,
        ),

        "preferred_citations": preferences.get(
            "preferred_citations",
            True,
        ),

        "interaction_count": profile.get(
            "interaction_count",
            0,
        ),

        "feedback_analysis": feedback_analysis,
    }
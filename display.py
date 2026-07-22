# display.py


def format_feature_name(feature_name):
    """
    Convert an internal feature name into readable text.

    Example:
        pool_table -> Pool table
        sports_tv -> Sports TV
    """

    special_labels = {
        "sports_tv": "Sports TV",
        "guinness": "Guinness",
    }

    if feature_name in special_labels:
        return special_labels[feature_name]

    return feature_name.replace("_", " ").capitalize()


def display_search_summary(
    occasion,
    preferences,
    maximum_distance,
):
    """
    Display the user's search choices before showing results.
    """

    print("\n" + "=" * 50)
    print("🔎 YOUR SEARCH")
    print("=" * 50)

    if isinstance(occasion, dict):
        occasion_name = (
            occasion.get("name")
            or occasion.get("label")
            or occasion.get("title")
            or "Custom occasion"
        )
    else:
        occasion_name = str(occasion)

    print(f"Occasion: {occasion_name}")
    print(f"Maximum distance: {maximum_distance} minutes")

    selected_preferences = []

    if isinstance(preferences, dict):
        for feature_name, preference_value in preferences.items():
            if preference_value in (None, False, "", "none", "no"):
                continue

            readable_feature = format_feature_name(feature_name)

            if isinstance(preference_value, dict):
                preference_level = (
                    preference_value.get("priority")
                    or preference_value.get("level")
                    or preference_value.get("importance")
                    or "selected"
                )
            else:
                preference_level = str(preference_value)

            selected_preferences.append(
                f"{readable_feature}: {preference_level}"
            )

    if selected_preferences:
        print("\nPreferences:")

        for preference in selected_preferences:
            print(f"  • {preference}")
    else:
        print("\nPreferences: None selected")


def display_score_breakdown(recommendation):
    """
    Display the points contributing to a recommendation's score.
    """

    score_breakdown = recommendation.get(
        "score_breakdown",
        {},
    )

    rating_score = score_breakdown.get("rating", 0)
    distance_score = score_breakdown.get("distance", 0)
    feature_score = score_breakdown.get("features", 0)

    print("\nScore breakdown:")
    print(f"  Rating: {rating_score:+.2f}")
    print(f"  Distance: {distance_score:+.2f}")
    print(f"  Preferences: {feature_score:+.2f}")

    feature_details = score_breakdown.get(
        "feature_details",
        {},
    )

    if feature_details:
        print("\nPreference details:")

        for feature_name, details in feature_details.items():
            readable_feature = format_feature_name(feature_name)

            if not isinstance(details, dict):
                continue

            preference_level = details.get(
                "preference",
                "selected",
            )

            matched = details.get(
                "matched",
                False,
            )

            points = details.get(
                "points",
                0,
            )

            symbol = "✓" if matched else "✗"

            print(
                f"  {symbol} {readable_feature} "
                f"({preference_level}): "
                f"{points:+}"
            )


def display_match_summary(recommendation):
    """
    Display features that matched or were missing.
    """

    matched_features = recommendation.get(
        "matched_features",
        [],
    )

    missing_features = recommendation.get(
        "missing_features",
        [],
    )

    if matched_features:
        print("\nMatches:")

        for feature_name in matched_features:
            print(
                f"  ✓ {format_feature_name(feature_name)}"
            )

    if missing_features:
        print("\nMissing preferences:")

        for feature_name in missing_features:
            print(
                f"  ✗ {format_feature_name(feature_name)}"
            )


def display_personality(recommendation):
    """
    Display personality information for a pub.
    """

    personality = recommendation.get(
        "personality",
        "Unknown",
    )

    description = recommendation.get(
        "personality_description",
        "",
    )

    personality_tags = recommendation.get(
        "personality_tags",
        [],
    )

    print(f"Personality: {personality}")

    if description:
        print(description)

    if personality_tags:
        readable_tags = ", ".join(
            str(tag)
            for tag in personality_tags
        )

        print(f"Tags: {readable_tags}")


def display_single_result(
    recommendation,
    position,
):
    """
    Display one ranked pub recommendation.
    """

    name = recommendation.get(
        "name",
        "Unknown pub",
    )

    rating = recommendation.get(
        "rating",
        0,
    )

    distance_minutes = recommendation.get(
        "distance_minutes",
        "Unknown",
    )

    score = recommendation.get(
        "score",
        0,
    )

    print("\n" + "-" * 50)
    print(f"#{position} — {name}")
    print("-" * 50)

    print(f"Rating: {rating}")
    print(f"Distance: {distance_minutes} minutes")
    print(f"Recommendation score: {score:.2f}")

    display_personality(recommendation)
    display_match_summary(recommendation)
    display_score_breakdown(recommendation)


def display_results(
    recommendations,
    maximum_results=3,
):
    """
    Display the highest-ranked pub recommendations.
    """

    print("\n" + "=" * 50)
    print("🍺 YOUR PINTFINDER RECOMMENDATIONS")
    print("=" * 50)

    if not recommendations:
        print(
            "\nNo pubs matched your search distance. "
            "Try increasing the maximum distance."
        )
        return

    results_to_display = recommendations[
        :maximum_results
    ]

    for position, recommendation in enumerate(
        results_to_display,
        start=1,
    ):
        display_single_result(
            recommendation,
            position,
        )

    print("\n" + "=" * 50)
# display.py


def format_readable_text(value):
    """Convert stored values into readable text."""
    return str(value).replace("_", " ").title()


def display_search_summary(
    occasion,
    preferences,
    maximum_distance,
):
    print("\n" + "=" * 50)
    print("SEARCH SUMMARY")
    print("=" * 50)

    print(f"Occasion: {occasion.get('name', 'Not specified')}")
    print(f"Maximum distance: {maximum_distance} minutes\n")

    print("Preferences:")

    active_preferences = False

    for feature, importance in preferences.items():

        if importance == "must":
            label = "Must have"
            active_preferences = True

        elif importance == "nice":
            label = "Nice to have"
            active_preferences = True

        else:
            label = "Don't care"

        print(
            f"• {format_readable_text(feature)}: {label}"
        )

    if not active_preferences:
        print(
            "\nNo specific features selected. Rankings will mainly be based "
            "on rating, distance and suitability for the occasion."
        )

    print("=" * 50)


def display_score_breakdown(pub):
    """Show exactly how the pub's score was calculated."""

    breakdown = pub.get("score_breakdown", {})
    feature_scores = breakdown.get("features", {})

    print("\nScore breakdown:")

    for feature, points in feature_scores.items():

        sign = "+" if points >= 0 else ""

        print(
            f"  {format_readable_text(feature)}: "
            f"{sign}{points:.1f}"
        )

    personality_points = breakdown.get("personality", 0)
    rating_points = breakdown.get("rating", 0)
    distance_points = breakdown.get("distance", 0)

    print(
        f"  Occasion atmosphere: "
        f"+{personality_points:.1f}"
    )

    print(
        f"  Rating: "
        f"+{rating_points:.1f}"
    )

    print(
        f"  Distance: "
        f"+{distance_points:.1f}"
    )


def display_results(results):

    print("\n🏆 Top Recommendations\n")

    if not results:
        print("No pubs were found within your selected distance.")
        return

    medals = ["🥇", "🥈", "🥉"]

    for index, pub in enumerate(results[:3]):

        position = index + 1

        if index < len(medals):
            ranking_label = medals[index]
        else:
            ranking_label = f"#{position}"

        print("=" * 60)
        print(
            f"{ranking_label} #{position}: "
            f"{pub.get('name', 'Unknown pub')}"
        )
        print("=" * 60)

        print(
            f"⭐ Rating: {pub.get('rating', 'Not available')}"
        )

        print(
            f"🚶 {pub.get('distance_minutes', 'Unknown')} mins away"
        )

        print(
            f"🍺 Personality: "
            f"{format_readable_text(pub.get('personality', 'unknown'))}"
        )

        personality_description = pub.get(
            "personality_description",
            "",
        )

        if personality_description:
            print(personality_description)

        personality_tags = pub.get("personality_tags", [])

        if personality_tags:
            print("\nTags:")

            for tag in personality_tags:
                print(
                    f"  • {format_readable_text(tag)}"
                )

        print(
            f"\nMatch Score: {pub.get('score', 0):.1f}"
        )

        print(f"\n💡 Why it is #{position}:")

        print(
            f"  {pub.get('ranking_explanation', 'No comparison available.')}"
        )

        matched_features = pub.get(
            "matched_features",
            [],
        )

        if matched_features:
            print("\n✅ Your preferences it meets:")

            for feature in matched_features:
                print(
                    f"  • {format_readable_text(feature)}"
                )

        missing_features = pub.get(
            "missing_features",
            [],
        )

        if missing_features:
            print("\n❌ Must-have preferences it misses:")

            for feature in missing_features:
                print(
                    f"  • {format_readable_text(feature)}"
                )

        display_score_breakdown(pub)

        print()
from explanations import generate_basic_summary
def format_feature_name(feature_name):
    """
    Convert an internal feature name into readable text.
    """

    special_labels = {
        "sports_tv": "Sports TV",
        "guinness": "Guinness",
        "dog_friendly": "Dog Friendly",
        "live_music": "Live Music",
        "beer_garden": "Outdoor Seating",
        "pool_table": "Pool Table",
    }

    return special_labels.get(
        feature_name,
        feature_name.replace("_", " ").title(),
    )
def format_price_level(price_level):
    """
    Convert Google's price enum into user-friendly text.
    """

    price_map = {
        "PRICE_LEVEL_FREE": "Free",
        "PRICE_LEVEL_INEXPENSIVE": "£ Inexpensive",
        "PRICE_LEVEL_MODERATE": "££ Moderate",
        "PRICE_LEVEL_EXPENSIVE": "£££ Expensive",
        "PRICE_LEVEL_VERY_EXPENSIVE": "££££ Very Expensive",
    }

    return price_map.get(price_level, price_level)

def display_search_summary(
    occasion,
    preferences,
    maximum_distance,
):
    print("\n" + "=" * 60)
    print("🔎 YOUR SEARCH")
    print("=" * 60)

    occasion_name = (
        occasion.get("name")
        if isinstance(occasion, dict)
        else str(occasion)
    )

    print(f"Occasion: {occasion_name}")
    print(f"Maximum distance: {maximum_distance} mins")

    selected = []

    for feature, value in preferences.items():

        if value in (
            None,
            False,
            "",
            "none",
            "no",
        ):
            continue

        selected.append(
            f"{format_feature_name(feature)} ({value})"
        )

    if selected:
        print("\nPreferences")

        for item in selected:
            print(f" • {item}")

    print()


def display_personality(recommendation):

    print(
        f"\n🧠 Personality: "
        f"{recommendation.get('personality', 'Unknown')}"
    )

    description = recommendation.get(
        "personality_description",
        "",
    )

    if description:
        print(description)

    tags = recommendation.get(
        "personality_tags",
        [],
    )

    if tags:
        print("\n🏷️ Best for")

        for tag in tags:
            print(f" • {tag}")

    confidence = recommendation.get(
        "personality_confidence",
        0,
    )

    if confidence:
        stars = (
            "★" * confidence
            + "☆" * (5 - confidence)
        )

        print(
            f"\nClassification confidence: {stars}"
        )


def display_google_details(recommendation):
    """
    Sprint 2 Google enrichment.
    """

    address = recommendation.get("address")
    website = recommendation.get("website")
    phone = recommendation.get("phone_number")
    maps = recommendation.get("google_maps_url")

    if not any(
        [
            address,
            website,
            phone,
            maps,
        ]
    ):
        return

    print("\n📍 Venue Information")

    if address:
        print(f"Address: {address}")

    if phone:
        print(f"Phone: {phone}")

    if website:
        print(f"Website: {website}")

    if maps:
        print(f"Google Maps: {maps}")


def display_google_features(recommendation):

    feature_icons = {
        "sports_tv": "⚽ Sports TV",
        "dog_friendly": "🐶 Dog Friendly",
        "food": "🍔 Food",
        "cocktails": "🍸 Cocktails",
        "live_music": "🎵 Live Music",
        "beer_garden": "🌳 Outdoor Seating",
    }

    enabled = []

    for feature, label in feature_icons.items():

        if recommendation.get(feature):
            enabled.append(label)

    open_now = recommendation.get("open_now")

    if open_now is True:
        enabled.append("🟢 Open Now")

    price = recommendation.get(
        "price_level"
    )

    if price:
        enabled.append(
            f"💰 {format_price_level(price)}"
        )

    if enabled:

        print("\nHighlights")

        for item in enabled:
            print(f" • {item}")


def display_match_summary(recommendation):

    matched = recommendation.get(
        "matched_features",
        [],
    )

    missing = recommendation.get(
        "missing_features",
        [],
    )

    if matched:

        print("\n✅ Matches")

        for feature in matched:
            print(
                f" • {format_feature_name(feature)}"
            )

    if missing:

        print("\n❌ Missing")

        for feature in missing:
            print(
                f" • {format_feature_name(feature)}"
            )


def display_score_breakdown(recommendation):

    breakdown = recommendation.get(
        "score_breakdown",
        {},
    )

    total = recommendation.get(
        "score",
        0,
    )

    print("\n📊 Recommendation Score\n")

    print(
        f" ⭐ Google Rating   "
        f"{breakdown.get('rating', 0):+6.0f}"
    )

    print(
        f" 🚶 Distance        "
        f"{breakdown.get('distance', 0):+6.0f}"
    )

    print(
        f" 🎯 Preferences     "
        f"{breakdown.get('features', 0):+6.0f}"
    )

    print(
    f" 🧠 Review Intelligence "
    f"{breakdown.get('reviews', 0):+6.0f}"
    )

    if breakdown.get("review_details"):
        for preference, points in breakdown["review_details"].items():
            print(f"    • {preference:<18} +{points}")
    

    print("\n" + "─" * 30)

    print(
        f" TOTAL              "
        f"{total:6.0f}"
    )

    

def display_single_result(
    recommendation,
    position,
):

    print("\n" + "=" * 60)

    print(
        f"#{position} "
        f"{recommendation.get('name')}"
    )

    print("=" * 60)

    print(
        f"⭐ Rating: "
        f"{recommendation.get('rating')}"
    )

    print(
        f"🚶 "
        f"{recommendation.get('distance_minutes')} mins away"
    )

    print(
        f"🏆 Score: "
        f"{recommendation.get('score'):.2f}"
    )
    print("\n💡 Why PintFinder recommends this\n")

    print(
        recommendation.get(
            "recommendation_summary",
            ""
        )
    )

    display_google_details(
        recommendation
    )

    display_google_features(
        recommendation
    )

    display_personality(
        recommendation
    )

    display_match_summary(
        recommendation
    )

    display_review_highlights(
        recommendation
    )

    display_score_breakdown(
        recommendation
    )
def display_review_highlights(
    recommendation,
):
    """
    Display the top insights extracted
    from customer reviews.
    """

    highlights = recommendation.get(
        "review_highlights",
        [],
    )

    if not highlights:
        return

    print("\n⭐ Why locals love it\n")

    for highlight in highlights:
        print(f" • {highlight}")

def display_results(
    recommendations,
    maximum_results=3,
):

    print("\n" + "=" * 60)
    print("🍺 PINTFINDER RECOMMENDATIONS")
    print("=" * 60)

    if not recommendations:

        print(
            "\nNo pubs found."
        )

        return

    for position, recommendation in enumerate(
        recommendations[:maximum_results],
        start=1,
    ):

        display_single_result(
            recommendation,
            position,
        )

    print("\n" + "=" * 60)
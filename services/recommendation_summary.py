def generate_recommendation_summary(
    pub,
    matched_features,
):
    """
    Generate a natural language summary
    explaining why this pub suits the user.
    """

    parts = []

    personality = getattr(
        pub,
        "personality",
        "Pub",
    )

    parts.append(
        f"{pub.name} is best described as a {personality.lower()}."
    )

    review_intelligence = getattr(
        pub,
        "review_intelligence",
        {},
    )

    if review_intelligence:

        top_features = sorted(
            review_intelligence.items(),
            key=lambda item: (
                item[1].get("strength", 0),
                item[1].get("confidence", 0),
            ),
            reverse=True,
        )[:3]

        readable = []

        DISPLAY_NAMES = {
            "beer_garden": "beer garden",
            "live_music": "live music",
            "food": "food",
            "cocktails": "cocktails",
            "guinness": "Guinness",
            "football": "football",
            "service": "friendly service",
            "value": "good value",
            "traditional": "traditional atmosphere",
            "lively": "lively atmosphere",
            "craft_beer": "craft beer",
            "rooftop": "rooftop",
            "views": "great views",
            "family_friendly": "family friendly atmosphere",
            "late_night": "late-night atmosphere",
            "quiet": "quiet atmosphere",
            "premium": "premium drinks",
            "sports": "sport",
            "cosy": "cosy atmosphere",
        }

        for key, _ in top_features:
            readable.append(
                DISPLAY_NAMES.get(
                    key,
                    key.replace("_", " ").lower(),
                )
            )

        if len(readable) == 1:
            parts.append(
                f"Locals consistently praise its {readable[0]}."
            )

        elif len(readable) == 2:
            parts.append(
                f"Locals consistently praise its {readable[0]} and {readable[1]}."
            )

        elif len(readable) >= 3:
            parts.append(
                f"Locals consistently praise its {readable[0]}, {readable[1]} and {readable[2]}."
            )

    if matched_features:

        readable = [
            feature.replace("_", " ").lower()
            for feature in matched_features
        ]

        if len(readable) == 1:
            parts.append(
                f"It matches your preference for {readable[0]}."
            )

        else:
            parts.append(
                "It matches your preferences for "
                + ", ".join(readable[:-1])
                + " and "
                + readable[-1]
                + "."
            )

    return " ".join(parts)
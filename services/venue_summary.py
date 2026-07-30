def generate_venue_summary(pub):
    """
    Create a natural language summary of a pub
    using all available PintFinder intelligence.
    """

    parts = []

    personality = getattr(pub, "personality", None)

    if personality:
        parts.append(
            f"{pub.name} is best described as a {personality.lower()}."
        )

    highlights = getattr(
        pub,
        "review_highlights",
        [],
    )

    if highlights:

        first_two = highlights[:2]

        readable = []

        for item in first_two:
            readable.append(
                item.split(" frequently")[0].lower()
            )

        parts.append(
            "Locals regularly praise "
            + " and ".join(readable)
            + "."
        )

    features = []

    if pub.beer_garden:
        features.append("outdoor seating")

    if pub.cocktails:
        features.append("cocktails")

    if pub.live_music:
        features.append("live music")

    if pub.dog_friendly:
        features.append("being dog friendly")

    if features:

        if len(features) == 1:
            feature_text = features[0]

        elif len(features) == 2:
            feature_text = (
                features[0]
                + " and "
                + features[1]
            )

        else:
            feature_text = (
                ", ".join(features[:-1])
                + " and "
                + features[-1]
            )

        parts.append(
            f"It also offers {feature_text}."
        )

    return " ".join(parts)
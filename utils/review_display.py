def stars(score):
    """
    Convert a review intelligence score into a 5-star rating.
    """

    if score >= 20:
        return "★★★★★"
    elif score >= 15:
        return "★★★★☆"
    elif score >= 10:
        return "★★★☆☆"
    elif score >= 5:
        return "★★☆☆☆"
    elif score > 0:
        return "★☆☆☆☆"

    return ""


def print_review_intelligence(pub_name, intelligence):
    """
    Pretty-print the extracted local intelligence.
    """

    print("\n" + "─" * 50)
    print(f"🧠 Local Intelligence — {pub_name}")
    print("─" * 50)

    ordered_categories = [
        "food",
        "beer_garden",
        "value",
        "service",
        "traditional",
        "craft_beer",
        "guinness",
        "lively",
        "quiet",
        "romantic",
        "premium",
    ]

    labels = {
        "food": "🍴 Food",
        "beer_garden": "🌳 Beer Garden",
        "value": "💰 Value",
        "service": "🙋 Service",
        "traditional": "🍺 Traditional Pub",
        "craft_beer": "🍻 Craft Beer",
        "guinness": "🟢 Guinness",
        "lively": "🎉 Atmosphere",
        "quiet": "😌 Quiet",
        "romantic": "❤️ Romantic",
        "premium": "✨ Premium",
    }

    for category in ordered_categories:

        data = intelligence.get(category)

        if data is None:
            continue

        if data["score"] == 0:
            continue
        
        print(f"\n{labels[category]}")
        print(stars(data["score"]))

        print(
            f"Mentioned by {data['mentions']} review(s)"
        )

        print(
            "Keywords: "
            + ", ".join(data["matches"])
        )
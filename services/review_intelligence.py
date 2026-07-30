from data.review_keywords import KEYWORDS

"""
Review intelligence engine.

Analyses Google reviews and extracts structured
signals about a venue.
"""


POSITIVE_WORDS = {
    "great",
    "excellent",
    "amazing",
    "fantastic",
    "lovely",
    "good",
    "friendly",
    "best",
    "perfect",
    "brilliant",
    "recommend",
    "recommended",
    "favourite",
    "favorite",
    "welcoming",
    "enjoyed",
    "delicious",
}

NEGATIVE_WORDS = {
    "bad",
    "poor",
    "awful",
    "terrible",
    "slow",
    "dirty",
    "expensive",
    "avoid",
    "worst",
    "disappointing",
    "disappointed",
    "rude",
    "overpriced",
    "unfriendly",
}


DISPLAY_NAMES = {
    "beer_garden": "Beer Garden",
    "live_music": "Live Music",
    "food": "Food",
    "cocktails": "Cocktails",
    "guinness": "Guinness",
    "football": "Football",
    "service": "Friendly Service",
    "value": "Good Value",
    "traditional": "Traditional Atmosphere",
    "lively": "Lively Atmosphere",
    "craft_beer": "Craft Beer",
    "rooftop": "Rooftop",
    "views": "Great Views",
    "family_friendly": "Family Friendly",
    "late_night": "Late Night",
    "quiet": "Quiet Atmosphere",
    "premium": "Premium Drinks",
    "pool_table": "Pool Table",
    "cosy": "Cosy Atmosphere",
}


def count_sentiment_hits(
    text,
):
    """
    Count simple positive and negative words
    within a review.
    """

    positive_hits = sum(
        word in text
        for word in POSITIVE_WORDS
    )

    negative_hits = sum(
        word in text
        for word in NEGATIVE_WORDS
    )

    return positive_hits, negative_hits


def analyse_reviews(
    reviews,
):
    """
    Analyse Google reviews and extract structured
    signals for each PintFinder review category.
    """

    results = {}

    if not isinstance(reviews, list):
        return results

    for category, keyword_items in KEYWORDS.items():
        score = 0
        mention_count = 0

        positive_review_count = 0
        negative_review_count = 0
        neutral_review_count = 0

        matched_displays = set()
        matched_phrases = set()
        review_examples = []

        for review in reviews:
            if not isinstance(review, dict):
                continue

            original_text = (
                review.get("text", {})
                .get("text", "")
            )

            if not isinstance(original_text, str):
                continue

            text = original_text.lower().strip()

            if not text:
                continue

            review_matched = False

            for item in keyword_items:
                if not isinstance(item, dict):
                    continue

                phrase = str(
                    item.get("phrase", "")
                ).lower().strip()

                weight = item.get(
                    "weight",
                    0,
                )

                display = item.get(
                    "display",
                    phrase,
                )

                if not phrase:
                    continue

                if not isinstance(
                    weight,
                    (int, float),
                ):
                    weight = 0

                phrase_words = phrase.split()

                if all(
                    word in text
                    for word in phrase_words
                ):
                    score += weight
                    matched_phrases.add(phrase)
                    matched_displays.add(display)
                    review_matched = True

            if not review_matched:
                continue

            mention_count += 1

            if len(review_examples) < 3:
                review_examples.append(
                    original_text
                )

            (
                positive_hits,
                negative_hits,
            ) = count_sentiment_hits(text)

            if positive_hits > negative_hits:
                positive_review_count += 1

            elif negative_hits > positive_hits:
                negative_review_count += 1

            else:
                neutral_review_count += 1

        if mention_count == 0:
            continue

        strength = min(
            100,
            max(
                0,
                round(
                    (score * 0.7)
                    + (mention_count * 5)
                ),
            ),
        )

        confidence = min(
            100,
            max(
                0,
                round(
                    strength
                    + (positive_review_count * 2)
                    - (negative_review_count * 4)
                ),
            ),
        )

        results[category] = {
            "score": score,
            "mentions": mention_count,
            "strength": strength,
            "confidence": confidence,
            "positive": positive_review_count,
            "negative": negative_review_count,
            "neutral": neutral_review_count,
            "matches": sorted(
                matched_displays
            ),
            "matched_phrases": sorted(
                matched_phrases
            ),
            "examples": review_examples,
        }

    return results


def generate_review_highlights(
    review_intelligence,
):
    """
    Convert review intelligence into short,
    user-friendly highlights.

    Only reasonably strong, predominantly positive
    themes are displayed.
    """

    highlights = []

    if not isinstance(
        review_intelligence,
        dict,
    ):
        return highlights

    sorted_features = sorted(
        review_intelligence.items(),
        key=lambda item: (
            item[1].get("strength", 0),
            item[1].get("confidence", 0),
            item[1].get("mentions", 0),
        ),
        reverse=True,
    )

    for key, data in sorted_features:
        if len(highlights) >= 5:
            break

        if not isinstance(data, dict):
            continue

        mentions = data.get(
            "mentions",
            0,
        )

        confidence = data.get(
            "confidence",
            0,
        )

        strength = data.get(
            "strength",
            0,
        )

        positive_reviews = data.get(
            "positive",
            0,
        )

        negative_reviews = data.get(
            "negative",
            0,
        )

        if mentions < 2:
            continue

        if confidence < 15:
            continue

        if strength < 15:
            continue

        if negative_reviews > positive_reviews:
            continue

        name = DISPLAY_NAMES.get(
            key,
            key.replace("_", " ").title(),
        )

        if negative_reviews > 0:
            wording = "receives mostly positive reviews"

        elif mentions >= 5:
            wording = "consistently praised"

        else:
            wording = "praised by reviewers"

        review_word = (
            "review"
            if mentions == 1
            else "reviews"
        )

        highlights.append(
            f"{name} {wording} "
            f"({mentions} {review_word})"
        )

    return highlights
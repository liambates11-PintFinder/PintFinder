from data.review_keywords import KEYWORDS

"""
Review intelligence engine.

Analyses Google reviews and extracts structured
signals about a venue.
"""



def analyse_reviews(reviews):
    results = {}

    for category, keyword_items in KEYWORDS.items():
        score = 0
        mention_count = 0
        matched_displays = set()
        matched_phrases = set()
        review_examples = []

        for review in reviews:
            text = review.get("text", {}).get("text", "").lower()

            if not text:
                continue

            review_matched = False

            for item in keyword_items:
                phrase = item["phrase"].lower()
                weight = item["weight"]
                display = item["display"]

                phrase_words = phrase.split()

                if all(word in text for word in phrase_words):
                    score += weight
                    matched_phrases.add(phrase)
                    matched_displays.add(display)
                    review_matched = True

            if review_matched:
                mention_count += 1

                if len(review_examples) < 3:
                    original_text = review.get("text", {}).get("text", "")
                    review_examples.append(original_text)

        if mention_count > 0:
            confidence = min(100, score + mention_count * 3)

            results[category] = {
                "score": score,
                "mentions": mention_count,
                "confidence": confidence,
                "matches": sorted(matched_displays),
                "matched_phrases": sorted(matched_phrases),
                "examples": review_examples,
            }

    return results
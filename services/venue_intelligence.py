"""
Venue Intelligence Engine.

Combines Google data, review intelligence and
heuristics into confidence scores.
"""


def calculate_feature_confidence(
    feature,
    google_value,
    review_confidence=0,
    personality=None,
):
    """
    Returns a confidence score (0-100)
    for a venue feature.
    """

    score = 0

    # Google confirmed
    if google_value is True:
        return 100

    # Review intelligence
    score += review_confidence

    # Personality heuristics
    if personality:

        if feature == "guinness":

            if personality == "🍺 Traditional Local":
                score += 30

            elif personality == "⚽ Sports Pub":
                score += 20

        elif feature == "pool_table":

            if personality == "🍺 Traditional Local":
                score += 20

            elif personality == "⚽ Sports Pub":
                score += 15

    return min(score, 100)
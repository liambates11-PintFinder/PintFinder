import random


def build_intro(matched):

    phrases = {
        "football": (
            "watch football",
            "watching football",
        ),
        "food": (
            "enjoy some food",
            "enjoying some food",
        ),
        "beer_garden": (
            "relax in a beer garden",
            "relaxing in a beer garden",
        ),
        "cocktails": (
            "enjoy cocktails",
            "enjoying cocktails",
        ),
        "guinness": (
            "enjoy a great pint of Guinness",
            "enjoying a great pint of Guinness",
        ),
        "live_music": (
            "listen to live music",
            "listening to live music",
        ),
        "dog_friendly": (
            "bring your dog along",
            "bringing your dog along",
        ),
    }

    activities = [
        phrases[f]
        for f in matched
        if f in phrases
    ]

    intro_starts = [
        "Perfect",
        "Perfect",
        "Ideal",
        "A great choice",
        "An excellent option",
    ]

    intro = random.choice(intro_starts)

    if not activities:
        return "A great nearby option."

    if len(activities) == 1:
        return (
            f"{intro} if you're looking to "
            f"{activities[0][0]}."
        )

    if len(activities) == 2:
        return (
            f"{intro} if you're looking to "
            f"{activities[0][0]} while "
            f"{activities[1][1]}."
        )

    return (
        f"{intro} if you're looking to "
        f"{activities[0][0]} while "
        f"{activities[1][1]} and "
        f"{activities[2][1]}."
    )



def generate_recommendation_summary(recommendation):
    """
    Generate a short explanation describing why this pub
    was recommended.
    """

    rating = recommendation.get("rating", 0)
    distance = recommendation.get("distance_minutes", 0)
    matched = recommendation.get("matched_features", [])

    opening = build_intro(matched)

    reasons = []

    # Google rating
    if rating >= 4.7:
        reasons.append(
            f"has an excellent {rating:.1f}★ Google rating"
        )
    elif rating >= 4.3:
        reasons.append(
            f"has a strong {rating:.1f}★ Google rating"
        ) 
    elif rating >= 4.0:
        reasons.append(
            f"has a solid {rating:.1f}★ Google rating"
        )

    # Distance
    if distance <= 5:
        reasons.append(
            f"is only a {distance}-minute walk away"
        )
    elif distance <= 10:
        reasons.append(
            f"is just an {distance}-minute walk away"
        )

    if not reasons:
        return opening

    if len(reasons) == 1:
        return (
            opening
            + "\n\nIt "
            + reasons[0]
            + "."
        )

    return (
        opening
        + "\n\nIt "
        + reasons[0]
        + " and "
        + reasons[1]
        + "."
    )
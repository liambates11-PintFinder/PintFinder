from dataclasses import dataclass


@dataclass
class PersonalityResult:
    personality: str
    description: str
    tags: list[str]
    confidence: int  # 1–5 stars


def classify_pub(pub) -> PersonalityResult:
    """
    Classify a pub using existing structured Google data.
    """

    # Convenience helpers
    sports = getattr(pub, "sports_tv", False)
    food = getattr(pub, "food", False)
    cocktails = getattr(pub, "cocktails", False)
    live_music = getattr(pub, "live_music", False)
    garden = getattr(pub, "beer_garden", False)
    dog = getattr(pub, "dog_friendly", False)

    price = getattr(pub, "price_level", "")
    rating = getattr(pub, "rating", 0)

    review_data = getattr(
        pub,
        "review_intelligence",
    {},
)

    def has_review_signal(feature):
        return (
            feature in review_data
            and review_data[feature]["confidence"] >= 20
        )

    scores = {
        "sports": 0,
        "traditional": 0,
        "cocktail": 0,
        "gastropub": 0,
        "beer_garden": 0,
        "live_music": 0,
        "hidden_gem": 0,
    }

    if sports:
        scores["sports"] += 5

    if has_review_signal("football"):
        scores["sports"] += 3

    if cocktails:
        scores["cocktail"] += 2

    if has_review_signal("cocktails"):
        scores["cocktail"] += 2

    if food:
        scores["gastropub"] += 2

    if price in (
        "PRICE_LEVEL_EXPENSIVE",
        "PRICE_LEVEL_VERY_EXPENSIVE",
    ):
        scores["gastropub"] += 3

    if garden:
        scores["beer_garden"] += 4

    if live_music:
        scores["live_music"] += 4

    if has_review_signal("live_music"):
        scores["live_music"] += 2

    if dog:
        scores["traditional"] += 1

    if has_review_signal("traditional"):
        scores["traditional"] += 3

    if has_review_signal("locals"):
        scores["traditional"] += 3

    if has_review_signal("real_ale"):
        scores["traditional"] += 2

    if has_review_signal("pool_table"):
        scores["traditional"] += 2

    if has_review_signal("guinness"):
        scores["traditional"] += 2

    if rating >= 4.7:
        scores["hidden_gem"] += 3


    highest_score = max(scores.values())

    if highest_score == 0:
        return PersonalityResult(
            personality="🍺 Classic Pub",
            description=(
                "A well-rounded pub offering a balanced experience."
            ),
            tags=["Pub"],
            confidence=2,
        )

    personality = max(
        scores,
        key=scores.get,
    )

    if personality == "sports":
        return PersonalityResult(
            personality="⚽ Sports Pub",
            description=(
                "A lively venue where live sport is a major attraction, ideal for watching the big match with friends."
            ),
            tags=["Sport", "Groups", "Beer"],
            confidence=min(5, max(2, scores["sports"])),
        )

    if personality == "traditional":
        return PersonalityResult(
            personality="🍺 Traditional Local",
            description=(
                "A welcoming neighbourhood pub with a traditional atmosphere, popular with locals."
            ),
            tags=["Traditional", "Local", "Community"],
            confidence=min(5, max(2, scores["traditional"])),
        )

    if personality == "cocktail":
        return PersonalityResult(
            personality="🍸 Cocktail Bar",
            description=(
                "A modern venue focused on cocktails and evening drinks."
            ),
            tags=["Cocktails", "Evening", "Modern"],
            confidence=min(5, max(2, scores["cocktail"])),
        )

    if personality == "gastropub":
        return PersonalityResult(
            personality="🍔 Gastropub",
            description=(
                "A food-led pub offering quality dining alongside drinks."
            ),
            tags=["Food", "Dining", "Quality"],
            confidence=min(5, max(2, scores["gastropub"])),
        )

    if personality == "beer_garden":
        return PersonalityResult(
            personality="🌿 Beer Garden Pub",
            description=(
                "A relaxed pub with outdoor space that's perfect in good weather."
            ),
            tags=["Outdoor", "Summer", "Relaxed"],
            confidence=min(5, max(2, scores["beer_garden"])),
        )

    if personality == "live_music":
        return PersonalityResult(
            personality="🎵 Live Music Venue",
            description=(
                "A social venue known for regular live entertainment."
            ),
            tags=["Music", "Evening", "Entertainment"],
            confidence=min(5, max(2, scores["live_music"])),
        )

    return PersonalityResult(
        personality="🍺 Classic Pub",
        description=(
            "A well-rounded pub offering a balanced experience."
        ),
        tags=["Pub"],
        confidence=2,
    )
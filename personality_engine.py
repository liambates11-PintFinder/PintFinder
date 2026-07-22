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

    # Sports Pub
    if sports:
        return PersonalityResult(
            personality="⚽ Sports Pub",
            description=(
                "A lively venue where live sport is a major attraction, "
                "ideal for watching the big match with friends."
            ),
            tags=["Sport", "Groups", "Beer"],
            confidence=4,
        )

    # Cocktail Bar
    if cocktails and not food:
        return PersonalityResult(
            personality="🍸 Cocktail Bar",
            description=(
                "A modern venue focused on cocktails and evening drinks."
            ),
            tags=["Cocktails", "Evening", "Modern"],
            confidence=4,
        )

    # Gastropub
    if food and price in (
        "PRICE_LEVEL_EXPENSIVE",
        "PRICE_LEVEL_VERY_EXPENSIVE",
    ):
        return PersonalityResult(
            personality="🍔 Gastropub",
            description=(
                "A food-led pub offering quality dining alongside drinks."
            ),
            tags=["Food", "Dining", "Quality"],
            confidence=4,
        )

    # Beer Garden Pub
    if garden:
        return PersonalityResult(
            personality="🌿 Beer Garden Pub",
            description=(
                "A relaxed pub with outdoor space that's perfect in good weather."
            ),
            tags=["Outdoor", "Summer", "Relaxed"],
            confidence=4,
        )

    # Live Music Venue
    if live_music:
        return PersonalityResult(
            personality="🎵 Live Music Venue",
            description=(
                "A social venue known for regular live entertainment."
            ),
            tags=["Music", "Evening", "Entertainment"],
            confidence=4,
        )

    # Traditional Local
    if dog and food:
        return PersonalityResult(
            personality="🍺 Traditional Local",
            description=(
                "A welcoming neighbourhood pub popular with locals, "
                "offering food and a relaxed atmosphere."
            ),
            tags=["Traditional", "Local", "Community"],
            confidence=4,
        )

    # Hidden Gem
    if rating >= 4.7:
        return PersonalityResult(
            personality="🌟 Hidden Gem",
            description=(
                "An exceptionally highly rated pub that stands out from the crowd."
            ),
            tags=["Highly Rated", "Recommended"],
            confidence=3,
        )

    return PersonalityResult(
        personality="🍺 Classic Pub",
        description=(
            "A well-rounded pub offering a balanced experience."
        ),
        tags=["Pub"],
        confidence=2,
    )
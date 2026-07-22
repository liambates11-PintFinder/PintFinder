from dataclasses import dataclass, field


@dataclass
class Pub:
    """
    Represents a pub within PintFinder.

    This model stores:
    - Core recommendation data
    - Google Places identifiers
    - AI-generated personality data
    - User-facing venue features
    """

    # Core information
    name: str
    rating: float
    distance_minutes: int

    # Google Places identifier
    place_id: str | None = None

    # AI enrichment
    personality: str = "Unclassified"
    personality_description: str = (
        "AI enrichment coming soon."
    )
    personality_tags: list[str] = field(default_factory=list)

    # Venue features
    pool_table: bool = False
    sports_tv: bool = False
    guinness: bool = False
    food: bool = False
    beer_garden: bool = False
    cocktails: bool = False
    dog_friendly: bool = False
    live_music: bool = False
    quiz: bool = False
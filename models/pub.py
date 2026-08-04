from dataclasses import dataclass, field


@dataclass
class Pub:
    """
    Represents a pub within PintFinder.
    """

    # Required core information
    name: str
    rating: float
    distance_minutes: int

    # Google identifiers and contact details
    place_id: str | None = None
    address: str | None = None
    website: str | None = None
    phone_number: str | None = None
    google_maps_url: str | None = None
    price_level: str | None = None
    open_now: bool | None = None

    # Personality information
    personality: str = "Unclassified"
    personality_description: str = (
        "Personality enrichment coming soon."
    )
    personality_tags: list[str] = field(
        default_factory=list
    )

    # Google-supported or partially supported features
    football: bool = False
    sports_tv: bool = False
    food: bool = False
    cocktails: bool = False
    dog_friendly: bool = False
    live_music: bool = False
    beer_garden: bool = False
    late_open: bool = False
    serves_beer: bool = False

    # Features requiring future custom enrichment
    pool_table: bool | None = None
    guinness: bool | None = None
    family_friendly: bool | None = None
    quiz_night: bool | None = None
    darts: bool | None = None
    craft_beer: bool | None = None

    pool_table_confidence: int = 0
    guinness_confidence: int = 0

    # Structured signals extracted from venue reviews
    review_intelligence: dict = field(default_factory=dict)
    review_highlights: list = field(default_factory=list)


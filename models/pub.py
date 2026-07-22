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
    pool_table: bool = False
    guinness: bool = False
    family_friendly: bool = False
    quiz_night: bool = False
    darts: bool = False
    craft_beer: bool = False
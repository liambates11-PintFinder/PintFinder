from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pub:
    name: str
    rating: float
    distance_minutes: int
    personality: str
    personality_description: str

    personality_tags: list = field(default_factory=list)

    # Google identification
    place_id: Optional[str] = None

    # Google business information
    address: Optional[str] = None
    google_maps_url: Optional[str] = None
    website: Optional[str] = None
    phone_number: Optional[str] = None
    price_level: Optional[str] = None
    user_rating_count: int = 0

    # Opening-hours information
    open_now: Optional[bool] = None
    opening_hours: list = field(default_factory=list)

    # PintFinder features
    pool_table: bool = False
    sports_tv: bool = False
    guinness: bool = False
    food: bool = False
    beer_garden: bool = False
    cocktails: bool = False
    dog_friendly: bool = False
    live_music: bool = False
    quiz: bool = False

    # Additional Google-provided information
    outdoor_seating: Optional[bool] = None
    serves_beer: Optional[bool] = None
    reservable: Optional[bool] = None
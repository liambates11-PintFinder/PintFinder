from dataclasses import dataclass, field


@dataclass
class Pub:

    name: str

    rating: float

    distance_minutes: int

    personality: str

    personality_description: str

    personality_tags: list = field(default_factory=list)

    pool_table: bool = False
    sports_tv: bool = False
    guinness: bool = False
    food: bool = False
    beer_garden: bool = False
    cocktails: bool = False
    dog_friendly: bool = False
    live_music: bool = False
    quiz: bool = False
# google_adapter.py

from math import radians, sin, cos, sqrt, atan2


def calculate_distance_minutes(
    user_lat,
    user_lng,
    pub_lat,
    pub_lng,
):
    """
    Approximate walking time using straight-line distance.
    We'll replace this later with Google's walking directions API.
    """

    R = 6371  # Earth's radius (km)

    dlat = radians(pub_lat - user_lat)
    dlng = radians(pub_lng - user_lng)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(user_lat))
        * cos(radians(pub_lat))
        * sin(dlng / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    km = R * c

    # Walking ≈ 12 minutes/km
    return round(km * 12)


def convert_google_pubs(
    google_pubs,
    user_lat,
    user_lng,
):
    """
    Convert Google Places into PintFinder format.
    """

    pubs = []

    for place in google_pubs:

        location = place.get("location", {})

        pubs.append(
            {
                "name": place["displayName"]["text"],
                "rating": place.get("rating", 0),

                "distance_minutes": calculate_distance_minutes(
                    user_lat,
                    user_lng,
                    location.get("latitude"),
                    location.get("longitude"),
                ),

                # Temporary defaults
                "personality": "traditional",

                "personality_description":
                    "Live Google pub (personality coming soon)",

                "personality_tags": [],

                # Default feature values
                "pool_table": False,
                "sports_tv": False,
                "guinness": False,
                "food": False,
                "beer_garden": False,
                "cocktails": False,
                "dog_friendly": False,
                "live_music": False,
                "quiz": False,
            }
        )

    return pubs
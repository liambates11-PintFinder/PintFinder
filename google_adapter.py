from math import radians, sin, cos, sqrt, atan2

from pub import Pub


def calculate_distance_minutes(
    user_lat,
    user_lng,
    pub_lat,
    pub_lng,
):
    """
    Approximate walking time using straight-line distance.
    """

    R = 6371

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

    return round(km * 12)


def convert_google_pubs(
    google_pubs,
    user_lat,
    user_lng,
):
    """
    Convert Google Places results into Pub objects.
    """

    pubs = []

    for place in google_pubs:

        location = place.get("location", {})

        pub = Pub(
            name=place["displayName"]["text"],
            rating=place.get("rating", 0),
            distance_minutes=calculate_distance_minutes(
                user_lat,
                user_lng,
                location.get("latitude"),
                location.get("longitude"),
            ),
            personality="Traditional",
            personality_description="Live Google pub (AI enrichment coming soon)",
            personality_tags=[],
        )

        pubs.append(pub)

    return pubs
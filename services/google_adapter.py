from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt

from models.pub import Pub


def calculate_distance_minutes(
    user_lat,
    user_lng,
    pub_lat,
    pub_lng,
):
    """
    Approximate walking time from straight-line distance.

    Assumes roughly 12 walking minutes per kilometre.
    """

    if (
        pub_lat is None
        or pub_lng is None
    ):
        return 0

    earth_radius_km = 6371

    latitude_difference = radians(
        pub_lat - user_lat
    )

    longitude_difference = radians(
        pub_lng - user_lng
    )

    haversine = (
        sin(latitude_difference / 2) ** 2
        + cos(radians(user_lat))
        * cos(radians(pub_lat))
        * sin(longitude_difference / 2) ** 2
    )

    central_angle = (
        2
        * atan2(
            sqrt(haversine),
            sqrt(1 - haversine),
        )
    )

    distance_km = (
        earth_radius_km
        * central_angle
    )

    return round(
        distance_km * 12
    )


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

        location = place.get(
            "location",
            {},
        )

        pub = Pub(
            name=place.get(
                "displayName",
                {},
            ).get(
                "text",
                "Unknown Pub",
            ),

            rating=place.get(
                "rating",
                0,
            ),

            distance_minutes=calculate_distance_minutes(
                user_lat,
                user_lng,
                location.get(
                    "latitude"
                ),
                location.get(
                    "longitude"
                ),
            ),

            place_id=place.get(
                "id"
            ),

            personality="Traditional",

            personality_description=(
                "Live Google pub "
                "(AI enrichment coming soon)"
            ),

            personality_tags=[],
        )

        pubs.append(
            pub
        )

    return pubs
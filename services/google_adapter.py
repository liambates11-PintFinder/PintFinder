from services.review_intelligence import generate_review_highlights

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
    Estimate walking time using straight-line distance.

    Assumes approximately 12 walking minutes per kilometre.
    """

    if pub_lat is None or pub_lng is None:
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

    return round(distance_km * 12)


def get_boolean_value(place, field_name):
    """
    Return a Google boolean when it is available.

    Missing Google fields currently fall back to False
    so they remain compatible with the existing scoring engine.
    """

    value = place.get(field_name)

    if isinstance(value, bool):
        return value

    return False


def is_open_late(place):
    """
    Estimate whether a pub stays open late.

    A pub is considered late-opening if any listed closing
    time is midnight or later.
    """

    opening_hours = place.get(
        "regularOpeningHours",
        {},
    )

    periods = opening_hours.get(
        "periods",
        [],
    )

    for period in periods:
        close_information = period.get(
            "close",
            {},
        )

        close_hour = close_information.get("hour")

        if not isinstance(close_hour, int):
            continue

        if close_hour == 0 or close_hour >= 23:
            return True

    return False


def convert_google_pubs(
    google_pubs,
    user_lat,
    user_lng,
):
    """
    Convert enriched Google Places dictionaries
    into PintFinder Pub objects.
    """

    pubs = []

    for place in google_pubs:
        location = place.get(
            "location",
            {},
        )

        display_name = place.get(
            "displayName",
            {},
        )

        pub = Pub(
            name=display_name.get(
                "text",
                "Unknown Pub",
            ),

            rating=float(
                place.get("rating", 0) or 0
            ),

            distance_minutes=calculate_distance_minutes(
                user_lat=user_lat,
                user_lng=user_lng,
                pub_lat=location.get("latitude"),
                pub_lng=location.get("longitude"),
            ),

            place_id=place.get("id"),

            address=place.get(
                "formattedAddress"
            ),

            website=place.get(
                "websiteUri"
            ),

            phone_number=place.get(
                "nationalPhoneNumber"
            ),

            google_maps_url=place.get(
                "googleMapsUri"
            ),

            price_level=place.get(
                "priceLevel"
            ),

            open_now=place.get(
                "currentOpeningHours",
                {},
            ).get(
                "openNow"
            ),

            personality="Unclassified",

            personality_description=(
                "Personality enrichment "
                "coming soon."
            ),

            personality_tags=[],

            # Google-supported features
            football=get_boolean_value(
                place,
                "goodForWatchingSports",
            ),

            sports_tv=get_boolean_value(
                place,
                "goodForWatchingSports",
            ),

            dog_friendly=get_boolean_value(
                place,
                "allowsDogs",
            ),

            live_music=get_boolean_value(
                place,
                "liveMusic",
            ),

            cocktails=get_boolean_value(
                place,
                "servesCocktails",
            ),

            food=get_boolean_value(
                place,
                "dineIn",
            ),

            # Outdoor seating is being used as the current
            # MVP proxy for a beer garden.
            beer_garden=get_boolean_value(
                place,
                "outdoorSeating",
            ),

            late_open=is_open_late(place),

            # Google confirms beer, but not specifically
            # craft beer or Guinness.
            serves_beer=get_boolean_value(
                place,
                "servesBeer",
            ),

            # Features enriched from review intelligence
            pool_table=place.get(
                "pool_table",
                None,
            ),

            guinness=place.get(
                "guinness",
                None,
            ),

            family_friendly=place.get(
                "family_friendly",
                None,
            ),

            quiz_night=place.get(
                "quiz_night",
                None,
            ),

            darts=place.get(
                "darts",
                None,
            ),

            craft_beer=place.get(
                "craft_beer",
                None,
            ),

            # PintFinder intelligence extracted from reviews
            review_intelligence=place.get(
                "review_intelligence",
                {},
            ),
            review_highlights=generate_review_highlights(
                place.get(
                    "review_intelligence",
                    {},
                )
            ),
        )

        pubs.append(pub)

    return pubs
from math import atan2, cos, radians, sin, sqrt

from models.pub import Pub


def calculate_distance_minutes(
    user_lat,
    user_lng,
    pub_lat,
    pub_lng,
):
    """
    Approximate walking time using straight-line distance.

    The estimate assumes approximately 12 walking minutes
    per kilometre.
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

    haversine_value = (
        sin(latitude_difference / 2) ** 2
        + cos(radians(user_lat))
        * cos(radians(pub_lat))
        * sin(longitude_difference / 2) ** 2
    )

    angular_distance = 2 * atan2(
        sqrt(haversine_value),
        sqrt(1 - haversine_value),
    )

    distance_km = (
        earth_radius_km
        * angular_distance
    )

    return round(distance_km * 12)


def get_display_name(place):
    """
    Safely extract a pub's display name.
    """

    display_name = place.get(
        "displayName",
        {},
    )

    return display_name.get(
        "text",
        "Unknown pub",
    )


def get_opening_hours(place):
    """
    Extract opening status and weekly opening-hours text.
    """

    regular_opening_hours = place.get(
        "regularOpeningHours",
        {},
    )

    open_now = regular_opening_hours.get(
        "openNow"
    )

    weekday_descriptions = (
        regular_opening_hours.get(
            "weekdayDescriptions",
            [],
        )
    )

    return (
        open_now,
        weekday_descriptions,
    )


def determine_food_availability(place):
    """
    Infer whether a venue serves food from Google dining fields.

    Google does not provide a generic 'servesFood' field, so
    PintFinder uses dine-in, lunch or dinner availability.
    """

    return any(
        (
            place.get("dineIn") is True,
            place.get("servesLunch") is True,
            place.get("servesDinner") is True,
        )
    )


def convert_google_pubs(
    google_pubs,
    user_lat,
    user_lng,
):
    """
    Convert enriched Google Places results into Pub objects.
    """

    pubs = []

    for place in google_pubs:
        location = place.get(
            "location",
            {},
        )

        pub_latitude = location.get(
            "latitude"
        )

        pub_longitude = location.get(
            "longitude"
        )

        open_now, opening_hours = (
            get_opening_hours(place)
        )

        pub = Pub(
            name=get_display_name(place),

            rating=place.get(
                "rating",
                0,
            ),

            user_rating_count=place.get(
                "userRatingCount",
                0,
            ),

            distance_minutes=calculate_distance_minutes(
                user_lat,
                user_lng,
                pub_latitude,
                pub_longitude,
            ),

            personality="Unclassified",

            personality_description=(
                "Live Google pub "
                "(personality enrichment coming soon)"
            ),

            personality_tags=[],

            place_id=place.get("id"),

            address=place.get(
                "formattedAddress"
            ),

            google_maps_url=place.get(
                "googleMapsUri"
            ),

            website=place.get(
                "websiteUri"
            ),

            phone_number=place.get(
                "nationalPhoneNumber"
            ),

            price_level=place.get(
                "priceLevel"
            ),

            open_now=open_now,

            opening_hours=opening_hours,

            # Existing PintFinder features
            food=determine_food_availability(
                place
            ),

            cocktails=(
                place.get("servesCocktails")
                is True
            ),

            dog_friendly=(
                place.get("allowsDogs")
                is True
            ),

            live_music=(
                place.get("liveMusic")
                is True
            ),

            sports_tv=(
                place.get(
                    "goodForWatchingSports"
                )
                is True
            ),

            # Keep outdoor seating separate from beer garden.
            # Outdoor seating does not guarantee a beer garden.
            outdoor_seating=place.get(
                "outdoorSeating"
            ),

            serves_beer=place.get(
                "servesBeer"
            ),

            reservable=place.get(
                "reservable"
            ),
        )

        pubs.append(pub)

    return pubs
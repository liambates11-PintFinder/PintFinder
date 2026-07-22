import os

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

NEARBY_SEARCH_URL = (
    "https://places.googleapis.com/v1/places:searchNearby"
)

PLACE_DETAILS_URL = (
    "https://places.googleapis.com/v1/places/{place_id}"
)

REQUEST_TIMEOUT_SECONDS = 15


def validate_api_key():
    """
    Ensure the Google Maps API key was loaded from .env.
    """

    if not API_KEY:
        raise RuntimeError(
            "GOOGLE_MAPS_API_KEY was not found. "
            "Check that it exists in your .env file."
        )


def get_nearby_pubs(
    latitude,
    longitude,
    radius=1500,
    maximum_results=20,
):
    """
    Return nearby pubs using Google Places API (New).

    This first request retrieves the information required to:
    - identify each pub
    - calculate distance
    - display basic rating information
    """

    validate_api_key()

    url = NEARBY_SEARCH_URL

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.rating,"
            "places.userRatingCount,"
            "places.location"
        ),
    }

    body = {
        "includedTypes": ["pub"],
        "maxResultCount": maximum_results,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": radius,
            }
        },
    }

    response = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    response.raise_for_status()

    data = response.json()

    return data.get("places", [])


def get_place_details(place_id):
    """
    Return additional information for one Google Place ID.

    Google Place Details requires fields without the 'places.'
    prefix used by Nearby Search.
    """

    validate_api_key()

    if not place_id:
        return {}

    url = PLACE_DETAILS_URL.format(
        place_id=place_id,
    )

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": (
            "id,"
            "formattedAddress,"
            "googleMapsUri,"
            "websiteUri,"
            "nationalPhoneNumber,"
            "regularOpeningHours,"
            "priceLevel,"
            "outdoorSeating,"
            "servesBeer,"
            "servesCocktails,"
            "servesLunch,"
            "servesDinner,"
            "dineIn,"
            "reservable,"
            "allowsDogs,"
            "liveMusic,"
            "goodForWatchingSports"
        ),
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    response.raise_for_status()

    return response.json()


def get_enriched_nearby_pubs(
    latitude,
    longitude,
    radius=1500,
    maximum_results=20,
):
    """
    Fetch nearby pubs and enrich each one with Place Details.

    A failed details request does not prevent all other pubs
    from being returned.
    """

    nearby_pubs = get_nearby_pubs(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        maximum_results=maximum_results,
    )

    enriched_pubs = []

    total_pubs = len(nearby_pubs)

    for position, nearby_pub in enumerate(
        nearby_pubs,
        start=1,
    ):
        place_id = nearby_pub.get("id")

        display_name = nearby_pub.get(
            "displayName",
            {},
        ).get(
            "text",
            "Unknown pub",
        )

        print(
            f"   Loading details "
            f"{position}/{total_pubs}: "
            f"{display_name}"
        )

        try:
            details = get_place_details(
                place_id,
            )

        except requests.RequestException as error:
            print(
                f"   ⚠️ Could not load details for "
                f"{display_name}: {error}"
            )

            details = {}

        # Nearby data supplies location and rating.
        # Details data supplies address, hours and amenities.
        combined_pub = {
            **nearby_pub,
            **details,
        }

        enriched_pubs.append(
            combined_pub
        )

    return enriched_pubs
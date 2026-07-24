from utils.review_display import print_review_intelligence
from pprint import pprint
import os

import requests
from dotenv import load_dotenv

from services.review_intelligence import analyse_reviews


load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

NEARBY_SEARCH_URL = (
    "https://places.googleapis.com/v1/"
    "places:searchNearby"
)

PLACE_DETAILS_URL = (
    "https://places.googleapis.com/v1/places"
)


def validate_api_key():
    """
    Ensure that a Google Maps API key has been configured.
    """

    if not API_KEY:
        raise RuntimeError(
            "GOOGLE_MAPS_API_KEY was not found. "
            "Add it to your .env file."
        )


def get_nearby_pubs(
    latitude,
    longitude,
    radius=1500,
    maximum_results=20,
):
    """
    Return nearby pubs using Google Nearby Search.
    """

    validate_api_key()

    maximum_results = max(
        1,
        min(int(maximum_results), 20),
    )

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
        NEARBY_SEARCH_URL,
        headers=headers,
        json=body,
        timeout=20,
    )

    response.raise_for_status()

    response_data = response.json()

    return response_data.get("places", [])

print("Calling Google Place Details...")

def get_place_details(place_id):
    """
    Retrieve details and supported venue features
    for one Google place.
    """

    validate_api_key()

    if not place_id:
        return {}

    url = f"{PLACE_DETAILS_URL}/{place_id}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": (
            "formattedAddress,"
            "websiteUri,"
            "nationalPhoneNumber,"
            "googleMapsUri,"
            "goodForWatchingSports,"
            "allowsDogs,"
            "liveMusic,"
            "outdoorSeating,"
            "servesBeer,"
            "servesCocktails,"
            "dineIn,"
            "currentOpeningHours,"
            "regularOpeningHours,"
            "priceLevel,"
            "reviews"
        ),
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()

    reviews = data.get("reviews", [])

    data["review_intelligence"] = analyse_reviews(reviews)

    pub_name = (
    data.get("displayName", {})
    .get("text", "Unknown Pub")
)

    print_review_intelligence(
    pub_name,
    data["review_intelligence"],
)

    return data


def get_enriched_nearby_pubs(
    latitude,
    longitude,
    radius=1500,
    maximum_results=20,
):
    """
    Search for nearby pubs and enrich each result
    using Google Place Details.

    This is the function imported by main.py.
    """

    nearby_pubs = get_nearby_pubs(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        maximum_results=maximum_results,
    )

    enriched_pubs = []

    for place in nearby_pubs:
        enriched_place = dict(place)

        place_id = place.get("id")

        if place_id:
            try:
                details = get_place_details(place_id)

                enriched_place.update(details)

            except requests.RequestException as error:
                pub_name = (
                    place.get("displayName", {})
                    .get("text", "Unknown pub")
                )

                print(
                    f"\n⚠️ Could not retrieve details "
                    f"for {pub_name}: {error}"
                )

        enriched_pubs.append(enriched_place)

    return enriched_pubs
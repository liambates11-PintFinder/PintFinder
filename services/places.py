import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


def get_nearby_pubs(
    latitude,
    longitude,
    radius=1500,
):
    """
    Return nearby pubs using the Google Places API (New).
    """

    url = (
        "https://places.googleapis.com/v1/"
        "places:searchNearby"
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
        "includedTypes": [
            "pub",
        ],
        "maxResultCount": 20,
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
        timeout=15,
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "places",
        [],
    )
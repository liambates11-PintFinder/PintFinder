# location.py

import os
import requests

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


def get_coordinates(location_text):
    """
    Converts a postcode or town into latitude/longitude.
    """

    url = "https://maps.googleapis.com/maps/api/geocode/json"

    response = requests.get(
        url,
        params={
            "address": location_text,
            "key": API_KEY,
        },
    )

    response.raise_for_status()

    data = response.json()

    if data["status"] != "OK":
        raise Exception(f"Geocoding failed: {data['status']}")

    location = data["results"][0]["geometry"]["location"]

    return (
        location["lat"],
        location["lng"],
    )
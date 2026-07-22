from features import FEATURES
from occasions import OCCASION_TEMPLATES

from validation import validate_database

from user_input import (
    ask_occasion,
    collect_preferences,
)

from recommendation_engine import calculate_recommendations

from display import (
    display_results,
    display_search_summary,
)

from services.location import get_coordinates
from services.places import get_nearby_pubs
from services.google_adapter import convert_google_pubs

from services.cache import (
    get_cached_results,
    save_results,
)


def main():

    print("=" * 50)
    print("🍺 Welcome to PintFinder")
    print("=" * 50)

    location = input("\nWhere are you?\n> ")

    latitude, longitude = get_coordinates(location)

    # Build a cache key
    cache_key = f"{location.lower()}_1500"

    # Try loading pubs from cache
    pubs = get_cached_results(cache_key)

    if pubs is None:

        print("\n🌐 Fetching pubs from Google...")

        google_pubs = get_nearby_pubs(
            latitude,
            longitude,
        )

        pubs = convert_google_pubs(
            google_pubs,
            latitude,
            longitude,
        )

        save_results(
            cache_key,
            pubs,
        )

    else:

        print("\n⚡ Loaded pubs from cache.")

    validate_database(
        pubs,
        FEATURES,
    )

    occasion = ask_occasion(
        OCCASION_TEMPLATES,
    )

    preferences, maximum_distance = collect_preferences(
        FEATURES,
        occasion,
    )

    display_search_summary(
        occasion,
        preferences,
        maximum_distance,
    )

    recommendations = calculate_recommendations(
        pubs,
        occasion,
        preferences,
        maximum_distance,
    )

    display_results(
        recommendations,
    )


if __name__ == "__main__":
    main()
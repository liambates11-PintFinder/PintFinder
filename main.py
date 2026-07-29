import traceback
from display import (
    display_results,
    display_search_summary,
)

from features import FEATURES
from occasions import OCCASION_TEMPLATES
from recommendation_engine import calculate_recommendations

from services.cache import (
    get_cached_results,
    save_results,
)

from services.google_adapter import (
    convert_google_pubs,
)

from services.location import get_coordinates

from services.places import (
    get_enriched_nearby_pubs,
)

from user_input import (
    ask_occasion,
    collect_preferences,
)

from validation import validate_database


SEARCH_RADIUS_METRES = 1500
MAXIMUM_GOOGLE_RESULTS = 20
CACHE_VERSION = "v3_review_intelligence"


def build_cache_key(location):
    """
    Build a normalized, versioned cache key.

    Changing CACHE_VERSION prevents older, non-enriched cached
    Pub objects from being loaded after the data model changes.
    """

    normalized_location = (
        location
        .strip()
        .lower()
    )

    return (
        f"{normalized_location}_"
        f"{SEARCH_RADIUS_METRES}_"
        f"{CACHE_VERSION}"
    )


def main():
    print("=" * 50)
    print("🍺 Welcome to PintFinder")
    print("=" * 50)

    location = input(
        "\nWhere are you?\n> "
    ).strip()

    if not location:
        print(
            "\nPlease enter a town, postcode "
            "or location."
        )
        return

    try:
        latitude, longitude = (
            get_coordinates(location)
        )

        cache_key = build_cache_key(
            location
        )

        pubs = get_cached_results(
            cache_key
        )

        if pubs is None:
            print(
                "\n🌐 Fetching pubs from Google..."
            )

            google_pubs = (
                get_enriched_nearby_pubs(
                    latitude=latitude,
                    longitude=longitude,
                    radius=SEARCH_RADIUS_METRES,
                    maximum_results=(
                        MAXIMUM_GOOGLE_RESULTS
                    ),
                )
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

            print(
                f"\n✅ Loaded and cached "
                f"{len(pubs)} enriched pubs."
            )

        else:
            print(
                "\n⚡ Loaded enriched pubs "
                "from cache."
            )

        validate_database(
            pubs,
            FEATURES,
        )

        occasion = ask_occasion(
            OCCASION_TEMPLATES,
        )

        (
            preferences,
            maximum_distance,
        ) = collect_preferences(
            FEATURES,
            occasion,
        )

        display_search_summary(
            occasion,
            preferences,
            maximum_distance,
        )

        recommendations = (
            calculate_recommendations(
                pubs,
                occasion,
                preferences,
                maximum_distance,
            )
        )

        display_results(
            recommendations,
        )


    except Exception as error:
        print("\n❌ PintFinder could not complete the search.")
        traceback.print_exc()
        print(f"\nReason: {error}")


if __name__ == "__main__":
    main()
from personality_engine import classify_pub
from typing import Any


MUST_MATCH_REWARD = 30
MUST_MISS_PENALTY = 40

NICE_MATCH_REWARD = 15
NICE_MISS_PENALTY = 0

RATING_MULTIPLIER = 5
MAX_DISTANCE_SCORE = 20


def get_preference_level(value: Any) -> str | None:
    """
    Convert different preference formats into a consistent level.

    Supported examples:
        "must"
        "nice"
        "must_have"
        "nice_to_have"
        True
        False
        {"priority": "must"}
        {"level": "nice"}
    """

    if isinstance(value, dict):
        value = (
            value.get("priority")
            or value.get("level")
            or value.get("preference")
            or value.get("importance")
        )

    if value is True:
        return "nice"

    if value in (False, None, "", "no", "none"):
        return None

    if not isinstance(value, str):
        return None

    normalized_value = (
        value.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    must_values = {
        "must",
        "must_have",
        "essential",
        "required",
        "very_important",
    }

    nice_values = {
        "nice",
        "nice_to_have",
        "preferred",
        "important",
        "yes",
    }

    if normalized_value in must_values:
        return "must"

    if normalized_value in nice_values:
        return "nice"

    return None


def extract_occasion_preferences(occasion: Any) -> dict:
    """
    Extract feature preferences from an occasion template.

    Supported occasion keys include:
        preferences
        feature_weights
        features
        recommended_features
    """

    if not isinstance(occasion, dict):
        return {}

    possible_keys = (
        "preferences",
        "feature_weights",
        "features",
        "recommended_features",
    )

    for key in possible_keys:
        occasion_preferences = occasion.get(key)

        if isinstance(occasion_preferences, dict):
            return occasion_preferences.copy()

    return {}


def combine_preferences(
    occasion: Any,
    user_preferences: Any,
) -> dict:
    """
    Combine occasion defaults with the user's selected preferences.

    User selections take priority over occasion defaults.
    """

    combined_preferences = extract_occasion_preferences(
        occasion
    )

    if isinstance(user_preferences, dict):
        combined_preferences.update(user_preferences)

    return combined_preferences


def calculate_rating_score(rating: Any) -> float:
    """
    Convert a Google rating into recommendation points.
    """

    if not isinstance(rating, (int, float)):
        return 0

    bounded_rating = max(
        0,
        min(float(rating), 5),
    )

    return round(
        bounded_rating * RATING_MULTIPLIER,
        2,
    )


def calculate_distance_score(
    distance_minutes: Any,
    maximum_distance: Any,
) -> float:
    """
    Award more points to closer pubs.

    A pub at zero minutes receives the maximum distance score.
    A pub at the maximum distance receives zero distance points.
    """

    if not isinstance(
        distance_minutes,
        (int, float),
    ):
        return 0

    if not isinstance(
        maximum_distance,
        (int, float),
    ):
        return 0

    if maximum_distance <= 0:
        return 0

    if distance_minutes > maximum_distance:
        return 0

    distance_ratio = (
        distance_minutes
        / maximum_distance
    )

    score = (
        MAX_DISTANCE_SCORE
        * (1 - distance_ratio)
    )

    return round(
        max(score, 0),
        2,
    )


def score_feature_preferences(
    pub: Any,
    preferences: dict,
) -> tuple[float, list, list, dict]:
    """
    Score a pub against the selected feature preferences.

    Returns:
        feature_score
        matched_features
        missing_features
        feature_breakdown
    """

    feature_score = 0
    matched_features = []
    missing_features = []
    feature_breakdown = {}

    for (
        feature_name,
        preference_value,
    ) in preferences.items():
        preference_level = get_preference_level(
            preference_value
        )

        if preference_level is None:
            continue

        pub_feature_value = getattr(
            pub,
            feature_name,
            None,
        )

        pub_has_feature = (
            pub_feature_value is True
        )

        if preference_level == "must":
            if pub_has_feature:
                points = MUST_MATCH_REWARD
                matched_features.append(
                    feature_name
                )
            else:
                points = -MUST_MISS_PENALTY
                missing_features.append(
                    feature_name
                )

        else:
            if pub_has_feature:
                points = NICE_MATCH_REWARD
                matched_features.append(
                    feature_name
                )
            else:
                points = -NICE_MISS_PENALTY
                missing_features.append(
                    feature_name
                )

        feature_score += points

        feature_breakdown[
            feature_name
        ] = {
            "preference": preference_level,
            "value": pub_feature_value,
            "matched": pub_has_feature,
            "points": points,
        }

    return (
        feature_score,
        matched_features,
        missing_features,
        feature_breakdown,
    )
def score_review_preferences(
    pub,
    combined_preferences,
):
    """
    Scores a pub using review intelligence.

    This will eventually use extracted Google review signals
    such as:
    - Great Guinness
    - Hidden Gem
    - Proper Local
    - Sunday Roast
    - Friendly Staff
    """

    preference_mapping = {
        "Craft Beer": "craft_beer",
        "Food": "food",
        "Beer Garden": "beer_garden",
        "Traditional Pub": "traditional",
        "Quiet": "quiet",
        "Service": "service",
    }

    review_score = 0
    review_breakdown = {}

    review_data = getattr(pub, "review_intelligence", {})

    for preference_name, importance in combined_preferences.items():

        if importance == "dont_care":
            continue

        review_key = preference_mapping.get(preference_name)

        if review_key is None:
            continue

        signal = review_data.get(review_key)

        if not signal:
            continue

        confidence = signal.get("confidence", 0)

        points = confidence / 20

        if importance == "must":
            points *= 2

        review_score += points

        review_breakdown[preference_name] = round(points, 1)

        print(pub.name)
        print(review_score)
        print(review_breakdown)
        print("-" * 40)
    return review_score, review_breakdown

def create_recommendation(
    pub: Any,
    score: float,
    matched_features: list,
    missing_features: list,
    score_breakdown: dict,
) -> dict:
    """
    Convert a Pub object into the dictionary expected
    by the display layer.
    """
    personality = classify_pub(pub)

    return {
        "pub": pub,

        # Core pub information
        "name": pub.name,
        "rating": pub.rating,
        "distance_minutes": (
            pub.distance_minutes
        ),
        "score": round(score, 2),

        # Google identifiers and venue details
        "place_id": getattr(
            pub,
            "place_id",
            None,
        ),
        "address": getattr(
            pub,
            "address",
            None,
        ),
        "website": getattr(
            pub,
            "website",
            None,
        ),
        "phone_number": getattr(
            pub,
            "phone_number",
            None,
        ),
        "google_maps_url": getattr(
            pub,
            "google_maps_url",
            None,
        ),
        "price_level": getattr(
            pub,
            "price_level",
            None,
        ),
        "open_now": getattr(
            pub,
            "open_now",
            None,
        ),

        # Google-supported features
        "football": getattr(
            pub,
            "football",
            None,
        ),
        "sports_tv": getattr(
            pub,
            "sports_tv",
            None,
        ),
        "dog_friendly": getattr(
            pub,
            "dog_friendly",
            None,
        ),
        "live_music": getattr(
            pub,
            "live_music",
            None,
        ),
        "cocktails": getattr(
            pub,
            "cocktails",
            None,
        ),
        "food": getattr(
            pub,
            "food",
            None,
        ),
        "beer_garden": getattr(
            pub,
            "beer_garden",
            None,
        ),
        "late_open": getattr(
            pub,
            "late_open",
            None,
        ),
        "serves_beer": getattr(
            pub,
            "serves_beer",
            None,
        ),

        # Future PintFinder enrichment
        "pool_table": getattr(
            pub,
            "pool_table",
            None,
        ),
        "guinness": getattr(
            pub,
            "guinness",
            None,
        ),
        "family_friendly": getattr(
            pub,
            "family_friendly",
            None,
        ),
        "quiz_night": getattr(
            pub,
            "quiz_night",
            None,
        ),
        "darts": getattr(
            pub,
            "darts",
            None,
        ),
        "craft_beer": getattr(
            pub,
            "craft_beer",
            None,
        ),
    
        # Personality
         
"personality": personality.personality,

"personality_description": personality.description,

"personality_tags": personality.tags,

"personality_confidence": personality.confidence,

        # Recommendation results
        "matched_features": (
            matched_features
        ),
        "missing_features": (
            missing_features
        ),
        "score_breakdown": (
            score_breakdown
        ),
    }


def calculate_recommendations(
    pubs,
    occasion,
    preferences,
    maximum_distance,
):
    """
    Calculate and rank PintFinder recommendations.

    Scoring currently considers:
        - Google rating
        - Distance
        - Must-have preferences
        - Nice-to-have preferences

    Pubs outside the user's maximum distance are excluded.

    Missing must-have features receive a penalty rather than
    automatically removing the pub.
    """

    combined_preferences = combine_preferences(
        occasion,
        preferences,
    )

    recommendations = []

    for pub in pubs:
        distance_minutes = getattr(
            pub,
            "distance_minutes",
            None,
        )

        if (
            isinstance(
                maximum_distance,
                (int, float),
            )
            and maximum_distance > 0
            and isinstance(
                distance_minutes,
                (int, float),
            )
            and distance_minutes > maximum_distance
        ):
            continue

        rating_score = calculate_rating_score(
            getattr(
                pub,
                "rating",
                0,
            )
        )

        distance_score = calculate_distance_score(
            distance_minutes,
            maximum_distance,
        )

        (
            feature_score,
            matched_features,
            missing_features,
            feature_breakdown,
        ) = score_feature_preferences(
            pub,
            combined_preferences,
        )

        (
            review_score,
            review_breakdown,
        ) = score_review_preferences(
            pub,
            combined_preferences,
        )


        total_score = (
            rating_score
            + distance_score
            + feature_score
            + review_score
        )

        score_breakdown = {
            "rating": rating_score,
            "distance": distance_score,
            "features": feature_score,
            "feature_details": feature_breakdown,
            "reviews": review_score,
            "review_details": review_breakdown,
            "total": round(
                total_score,
                2,
            ),
        }

        recommendation = create_recommendation(
            pub=pub,
            score=total_score,
            matched_features=matched_features,
            missing_features=missing_features,
            score_breakdown=score_breakdown,
        )

        recommendations.append(
            recommendation
        )

    recommendations.sort(
        key=lambda recommendation: (
            recommendation["score"],
            recommendation["rating"],
            -recommendation["distance_minutes"],
        ),
        reverse=True,
    )

    return recommendations
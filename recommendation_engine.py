from personality_engine import classify_pub
from typing import Any
from services.recommendation_summary import (
    generate_recommendation_summary,
)


REVIEW_KEY_MAP = {
    "late_open": "late_night",
    "beer_garden": "beer_garden",
    "guinness": "guinness",
    "food": "food",
    "football": "football",
    "live_music": "live_music",
    "craft_beer": "craft_beer",
    "family_friendly": "family_friendly",
    "dog_friendly": "dog_friendly",
    "cocktails": "cocktails",
    "pool_table": "pool_table",
    "quiz_night": "quiz_night",
    "darts": "darts",
}

ESSENTIAL_MATCH_REWARD = 100
ESSENTIAL_MISS_PENALTY = 80

MUST_MATCH_REWARD = 40
MUST_MISS_PENALTY = 40

NICE_MATCH_REWARD = 15
NICE_MISS_PENALTY = 10


MUST_MATCH_REWARD = 40
MUST_MISS_PENALTY = 40

NICE_MATCH_REWARD = 15
NICE_MISS_PENALTY = 10

RATING_MULTIPLIER = 5
MAX_DISTANCE_SCORE = 10


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

    essential_values = {
        "essential",
    }

    must_values = {
        "must",
        "must_have",
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

    if normalized_value in essential_values:
        return "essential"

    if normalized_value in must_values:
        return "must"

    if normalized_value in nice_values:
        return "nice"

    return None



def extract_occasion_preferences(occasion: Any) -> dict:
    """
    Extract both default and locked preferences
    from a PintFinder occasion template.
    """
    if not isinstance(occasion, dict):
        return {}

    preferences = occasion.get(
        "default_preferences", {}
    ).copy()

    preferences.update(
        occasion.get("locked_preferences", {})
    )

    return preferences


def combine_preferences(
    occasion: Any,
    user_preferences: Any,
) -> dict:
    """
    Combine occasion defaults with user preferences.

    User preferences override defaults, but cannot
    override locked occasion requirements.
    """
    combined_preferences = extract_occasion_preferences(
        occasion
    )

    if isinstance(user_preferences, dict):
        combined_preferences.update(user_preferences)

    if isinstance(occasion, dict):
        combined_preferences.update(
            occasion.get("locked_preferences", {})
        )

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

    for feature_name, preference_value in preferences.items():

        preference_level = get_preference_level(preference_value)

        if preference_level is None:
            continue

        pub_feature_value = getattr(pub, feature_name, None)

        confidence = getattr(
            pub,
            f"{feature_name}_confidence",
            None,
        )

        if pub_feature_value is True:
            match_score = 1.0
        elif pub_feature_value is False:
            match_score = 0.0
        elif isinstance(confidence, (int, float)) and confidence > 0:
            match_score = max(0.0, min(confidence / 100, 1.0))
        else:
            match_score = 0.0

        pub_has_feature = match_score >= 0.5


        if preference_level == "essential":

            points = round(
                (match_score * ESSENTIAL_MATCH_REWARD)
                - ((1 - match_score) * ESSENTIAL_MISS_PENALTY)
            )

        elif preference_level == "must":

            points = round(
                (match_score * MUST_MATCH_REWARD)
                - ((1 - match_score) * MUST_MISS_PENALTY)
            )

        else:

            points = round(
                (match_score * NICE_MATCH_REWARD)
                - ((1 - match_score) * NICE_MISS_PENALTY)
            )

        if pub_has_feature:
            matched_features.append(feature_name)
        else:
            missing_features.append(feature_name)

        print(
            feature_name,
            "| confidence:",
            confidence,
            "| match:",
            round(match_score, 2),
            "| points:",
            points,
        )

        feature_score += points

        feature_breakdown[feature_name] = {
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
    Score a pub using review intelligence.
    """

    review_score = 0
    review_breakdown = {}
    matched_review_features = []

    review_data = getattr(
    pub,
    "review_intelligence",
    {},
)

    for preference_name, importance in combined_preferences.items():

        if importance == "dont_care":
            continue

        review_key = REVIEW_KEY_MAP.get(
        preference_name,
        preference_name,
    )

        if review_key not in review_data:
            continue

        confidence = review_data[review_key]["confidence"]

        if confidence < 15:
            continue

        points = round(confidence / 10)

        if importance == "must":
            points *= 2

        review_score += points

        review_breakdown[preference_name] = points

        matched_review_features.append(
            preference_name
        )

    return (
    review_score,
    review_breakdown,
    matched_review_features,
)

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

        # Review highlights
        "review_highlights": getattr(
            pub,
            "review_highlights",
            [],
        ),

        "recommendation_summary": generate_recommendation_summary(
            pub,
            matched_features
        ),

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
            matched_review_features,
        ) = score_review_preferences(
            pub,
            combined_preferences,
        )

        for feature in matched_review_features:
                preference_level = get_preference_level(
                    combined_preferences.get(feature)
                )

                if preference_level is None:
                    continue

                if feature not in matched_features:
                    matched_features.append(feature)

                if feature in missing_features:
                    missing_features.remove(feature)

                previous_points = (
                    feature_breakdown
                    .get(feature, {})
                    .get("points", 0)
                )

                if preference_level == "essential":
                    corrected_points = ESSENTIAL_MATCH_REWARD

                elif preference_level == "must":
                    corrected_points = MUST_MATCH_REWARD

                else:
                    corrected_points = NICE_MATCH_REWARD

                feature_score += (
                    corrected_points
                    - previous_points
                )

                feature_breakdown[feature] = {
                "preference": preference_level,
                "value": True,
                "matched": True,
                "source": "reviews",
                "points": corrected_points,
            }

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

        print(
            "Added:",
            recommendation["name"],
            recommendation["score"],
        )

        recommendations.append(
                recommendation
        )

    print(f"\nPubs scored: {len(recommendations)}")

    for recommendation in recommendations:
        print(
            recommendation["name"],
            recommendation["score"],
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
# recommendation_engine.py

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

    The function is intentionally flexible so it can support occasion
    dictionaries with keys such as:

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
            return occasion_preferences

    return {}


def combine_preferences(
    occasion: Any,
    user_preferences: Any,
) -> dict:
    """
    Combine occasion defaults with the user's selected preferences.

    User selections take priority over occasion defaults.
    """

    combined_preferences = extract_occasion_preferences(occasion)

    if isinstance(user_preferences, dict):
        combined_preferences.update(user_preferences)

    return combined_preferences


def calculate_rating_score(rating: Any) -> float:
    """
    Convert a Google rating into recommendation points.
    """

    if not isinstance(rating, (int, float)):
        return 0

    bounded_rating = max(0, min(float(rating), 5))

    return round(bounded_rating * RATING_MULTIPLIER, 2)


def calculate_distance_score(
    distance_minutes: Any,
    maximum_distance: Any,
) -> float:
    """
    Award more points to closer pubs.

    A pub at zero minutes receives the maximum distance score.
    A pub at the user's maximum distance receives zero distance points.
    """

    if not isinstance(distance_minutes, (int, float)):
        return 0

    if not isinstance(maximum_distance, (int, float)):
        return 0

    if maximum_distance <= 0:
        return 0

    if distance_minutes > maximum_distance:
        return 0

    distance_ratio = distance_minutes / maximum_distance

    score = MAX_DISTANCE_SCORE * (1 - distance_ratio)

    return round(max(score, 0), 2)


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

        pub_has_feature = bool(
            getattr(pub, feature_name, False)
        )

        if preference_level == "must":
            if pub_has_feature:
                points = MUST_MATCH_REWARD
                matched_features.append(feature_name)
            else:
                points = -MUST_MISS_PENALTY
                missing_features.append(feature_name)

        else:
            if pub_has_feature:
                points = NICE_MATCH_REWARD
                matched_features.append(feature_name)
            else:
                points = -NICE_MISS_PENALTY
                missing_features.append(feature_name)

        feature_score += points

        feature_breakdown[feature_name] = {
            "preference": preference_level,
            "matched": pub_has_feature,
            "points": points,
        }

    return (
        feature_score,
        matched_features,
        missing_features,
        feature_breakdown,
    )


def create_recommendation(
    pub: Any,
    score: float,
    matched_features: list,
    missing_features: list,
    score_breakdown: dict,
) -> dict:
    """
    Convert a Pub object into the recommendation dictionary expected
    by the display layer.
    """

    return {
        "pub": pub,
        "name": pub.name,
        "rating": pub.rating,
        "distance_minutes": pub.distance_minutes,
        "personality": pub.personality,
        "personality_description": pub.personality_description,
        "personality_tags": list(pub.personality_tags),
        "score": round(score, 2),
        "matched_features": matched_features,
        "missing_features": missing_features,
        "score_breakdown": score_breakdown,
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
    Missing must-have features receive a large penalty rather than
    automatically removing the pub.
    """

    combined_preferences = combine_preferences(
        occasion,
        preferences,
    )

    recommendations = []

    for pub in pubs:
        distance_minutes = pub.distance_minutes

        if (
            isinstance(maximum_distance, (int, float))
            and maximum_distance > 0
            and distance_minutes > maximum_distance
        ):
            continue

        rating_score = calculate_rating_score(
            pub.rating
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

        total_score = (
            rating_score
            + distance_score
            + feature_score
        )

        score_breakdown = {
            "rating": rating_score,
            "distance": distance_score,
            "features": feature_score,
            "feature_details": feature_breakdown,
            "total": round(total_score, 2),
        }

        recommendation = create_recommendation(
            pub=pub,
            score=total_score,
            matched_features=matched_features,
            missing_features=missing_features,
            score_breakdown=score_breakdown,
        )

        recommendations.append(recommendation)

    recommendations.sort(
        key=lambda recommendation: (
            recommendation["score"],
            recommendation["rating"],
            -recommendation["distance_minutes"],
        ),
        reverse=True,
    )

    return recommendations
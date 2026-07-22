# recommendation_engine.py


def format_feature_name(feature):
    """Convert a feature key into readable text."""
    return feature.replace("_", " ").title()


def build_comparison_explanation(pub, next_pub):
    """
    Explain why one pub ranks above the pub immediately below it.

    The explanation focuses on the score components that created
    the largest differences between the two pubs.
    """

    if next_pub is None:
        return "This is the final recommendation in the current shortlist."

    advantages = []
    disadvantages = []

    pub_breakdown = pub.get("score_breakdown", {})
    next_breakdown = next_pub.get("score_breakdown", {})

    # Compare selected feature scores
    feature_scores = pub_breakdown.get("features", {})
    next_feature_scores = next_breakdown.get("features", {})

    all_features = set(feature_scores) | set(next_feature_scores)

    for feature in all_features:
        difference = (
            feature_scores.get(feature, 0)
            - next_feature_scores.get(feature, 0)
        )

        readable_feature = format_feature_name(feature)

        if difference > 0:
            advantages.append(
                {
                    "difference": difference,
                    "text": (
                        f"it performs better for your "
                        f"{readable_feature} preference"
                    ),
                }
            )

        elif difference < 0:
            disadvantages.append(
                {
                    "difference": abs(difference),
                    "text": (
                        f"{next_pub.get('name', 'the next pub')} performs "
                        f"better for {readable_feature}"
                    ),
                }
            )

    # Compare personality score
    personality_difference = (
        pub_breakdown.get("personality", 0)
        - next_breakdown.get("personality", 0)
    )

    if personality_difference > 0:
        advantages.append(
            {
                "difference": personality_difference,
                "text": "it better matches the atmosphere for this occasion",
            }
        )

    elif personality_difference < 0:
        disadvantages.append(
            {
                "difference": abs(personality_difference),
                "text": (
                    f"{next_pub.get('name', 'the next pub')} better matches "
                    f"the atmosphere for this occasion"
                ),
            }
        )

    # Compare rating score
    rating_difference = (
        pub_breakdown.get("rating", 0)
        - next_breakdown.get("rating", 0)
    )

    if rating_difference > 0:
        advantages.append(
            {
                "difference": rating_difference,
                "text": (
                    f"it has the stronger rating "
                    f"({pub.get('rating', 'unknown')} versus "
                    f"{next_pub.get('rating', 'unknown')})"
                ),
            }
        )

    elif rating_difference < 0:
        disadvantages.append(
            {
                "difference": abs(rating_difference),
                "text": (
                    f"{next_pub.get('name', 'the next pub')} has the stronger "
                    f"rating ({next_pub.get('rating', 'unknown')} versus "
                    f"{pub.get('rating', 'unknown')})"
                ),
            }
        )

    # Compare distance score
    distance_difference = (
        pub_breakdown.get("distance", 0)
        - next_breakdown.get("distance", 0)
    )

    if distance_difference > 0:
        advantages.append(
            {
                "difference": distance_difference,
                "text": (
                    f"it is closer "
                    f"({pub.get('distance_minutes', 'unknown')} minutes versus "
                    f"{next_pub.get('distance_minutes', 'unknown')} minutes)"
                ),
            }
        )

    elif distance_difference < 0:
        disadvantages.append(
            {
                "difference": abs(distance_difference),
                "text": (
                    f"{next_pub.get('name', 'the next pub')} is closer "
                    f"({next_pub.get('distance_minutes', 'unknown')} minutes "
                    f"versus {pub.get('distance_minutes', 'unknown')} minutes)"
                ),
            }
        )

    # Show the most important differences first
    advantages.sort(
        key=lambda item: item["difference"],
        reverse=True,
    )

    disadvantages.sort(
        key=lambda item: item["difference"],
        reverse=True,
    )

    score_gap = pub.get("score", 0) - next_pub.get("score", 0)
    next_pub_name = next_pub.get("name", "the next recommendation")

    if not advantages:
        return (
            f"It is only narrowly above {next_pub_name}, with a score gap of "
            f"{score_gap:.1f} points. Their scores are otherwise very similar."
        )

    main_advantages = [item["text"] for item in advantages[:2]]

    if len(main_advantages) == 1:
        advantage_text = main_advantages[0]
    else:
        advantage_text = (
            f"{main_advantages[0]} and {main_advantages[1]}"
        )

    explanation = (
        f"It ranks {score_gap:.1f} points above {next_pub_name} mainly because "
        f"{advantage_text}."
    )

    if disadvantages:
        explanation += (
            f" However, {disadvantages[0]['text']}."
        )

    return explanation


def calculate_recommendations(
    pubs,
    occasion,
    preferences,
    maximum_distance,
):
    """
    Score pubs, rank them and explain why each pub is above the next one.
    """

    recommendations = []

    preferred_personalities = occasion.get(
        "preferred_personalities",
        [],
    )

    for pub in pubs:

        distance_minutes = pub.get("distance_minutes")

        # Skip pubs with no usable distance data
        if distance_minutes is None:
            continue

        # Filter pubs outside the chosen walking distance
        if distance_minutes > maximum_distance:
            continue

        score = 0
        matched_features = []
        missing_features = []
        feature_breakdown = {}

        # Score the user's selected preferences
        for feature, importance in preferences.items():

            if importance == "dont_care":
                continue

            has_feature = pub.get(feature, False)
            feature_score = 0

            if importance == "must":

                if has_feature:
                    feature_score = 30
                    matched_features.append(feature)
                else:
                    feature_score = -40
                    missing_features.append(feature)

            elif importance == "nice":

                if has_feature:
                    feature_score = 15
                    matched_features.append(feature)

            score += feature_score
            feature_breakdown[feature] = feature_score

        # Personality score
        personality = pub.get("personality")
        personality_score = 0

        if personality in preferred_personalities:
            personality_score = 20
            score += personality_score

        # Rating score
        rating = pub.get("rating", 0)
        rating_score = rating * 5
        score += rating_score

        # Distance score
        distance_score = max(0, 20 - distance_minutes)
        score += distance_score

        recommendations.append(
            {
                **pub,
                "score": score,
                "matched_features": matched_features,
                "missing_features": missing_features,
                "score_breakdown": {
                    "features": feature_breakdown,
                    "personality": personality_score,
                    "rating": rating_score,
                    "distance": distance_score,
                },
            }
        )

    recommendations.sort(
        key=lambda pub: pub.get("score", 0),
        reverse=True,
    )

    # Add ranking position and a direct comparison with the next pub
    for index, pub in enumerate(recommendations):

        pub["rank"] = index + 1

        next_pub = None

        if index + 1 < len(recommendations):
            next_pub = recommendations[index + 1]

        pub["ranking_explanation"] = build_comparison_explanation(
            pub,
            next_pub,
        )

    return recommendations
# validation.py


def validate_database(pubs, features):
    """
    Validate that every Pub object contains all fields
    required by PintFinder.
    """

    required_fields = {
        "name",
        "rating",
        "distance_minutes",
        "personality",
        "personality_description",
        "personality_tags",
    }

    for feature in features:
        if isinstance(feature, str):
            required_fields.add(feature)

        elif isinstance(feature, dict):
            feature_name = feature.get("key") or feature.get("name")

            if feature_name:
                required_fields.add(feature_name)

    for index, pub in enumerate(pubs, start=1):
        missing_fields = {
            field_name
            for field_name in required_fields
            if not hasattr(pub, field_name)
        }

        if missing_fields:
            missing_list = ", ".join(sorted(missing_fields))

            raise ValueError(
                f"Pub #{index} is missing required fields: "
                f"{missing_list}"
            )

    print(f"\n✅ Validated {len(pubs)} pubs.")
# validation.py

def validate_database(pubs, features):
    """
    Checks that every pub contains all required keys.
    Prints warnings instead of crashing if something is missing.
    """

    required_keys = {
        "name",
        "rating",
        "distance_minutes",
        "personality",
        "personality_description",
        "personality_tags",
    }

    for feature in features:
        required_keys.add(feature["database_key"])

    for pub in pubs:
        missing = required_keys - pub.keys()

        if missing:
            print(
                f"Warning: {pub['name']} is missing: "
                + ", ".join(sorted(missing))
            )
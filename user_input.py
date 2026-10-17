# user_input.py


def ask_occasion(occasion_templates):
    print("\nWhat are you going to the pub for?\n")

    for key, occasion in occasion_templates.items():
        print(f"{key}. {occasion['name']}")

    while True:
        choice = input("\nChoose an option: ")

        if choice in occasion_templates:
            return occasion_templates[choice]

        print("Invalid selection. Please try again.")


def ask_preference(feature_name, default):
    default_text = {
        "essential": "Essential",
        "must": "Must have",
        "nice": "Nice to have",
        "dont_care": "Don't care"
    }

    print(f"\n{feature_name.replace('_', ' ').title()}")

    print(f"Press Enter to keep default ({default_text[default]})")

    print("1. Essential")
    print("2. Must have")
    print("3. Nice to have")
    print("4. Don't care")

    choice = input("> ").strip()

    if choice == "":
        return default

    mapping = {
        "1": "essential",
        "2": "must",
        "3": "nice",
        "4": "dont_care"
    }

    return mapping.get(choice, default)



def ask_maximum_distance():
    while True:
        try:
            distance = int(
                input("\nMaximum walking distance (minutes): ")
            )

            if distance > 0:
                return distance

        except ValueError:
            pass

        print("Please enter a valid number.")


def collect_preferences(features, occasion):
    """
    Collect user preferences based on the selected occasion.

    Every feature starts as "don't care".
    Locked preferences are applied automatically.
    Only the occasion's default preferences are asked about.
    """

    preferences = {}

    # Start with every feature as "don't care"
    for feature in features:
        preferences[feature["database_key"]] = "dont_care"

    # Apply locked preferences
    for key, value in occasion["locked_preferences"].items():
        preferences[key] = value

    # Ask only about relevant features
    for key, default in occasion["default_preferences"].items():

        feature = next(
            f for f in features
            if f["database_key"] == key
        )

        preferences[key] = ask_preference(
            feature["summary_name"],
            default
        )

    maximum_distance = ask_maximum_distance()

    return preferences, maximum_distance
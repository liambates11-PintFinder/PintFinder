# occasions.py

OCCASION_TEMPLATES = {
    "1": {
        "name": "Watching football",
        "locked_preferences": {
            "football": "essential"
        },
        "default_preferences": {
            "guinness": "nice",
            "beer_garden": "dont_care",
            "food": "nice"
        },
        "preferred_personalities": [
            "Traditional sports pub",
            "No-frills sports and games pub"
        ]
    },
    "2": {
        "name": "Pool with friends",
        "locked_preferences": {
            "pool_table": "essential"
        },
        "default_preferences": {
            "football": "dont_care",
            "guinness": "nice",
            "late_open": "nice"
        },
        "preferred_personalities": [
            "Lively games pub",
            "No-frills sports and games pub"
        ]
    },
    "3": {
        "name": "Casual drinks",
        "locked_preferences": {},
        "default_preferences": {
            "beer_garden": "nice",
            "cocktails": "dont_care",
            "food": "dont_care"
        },
        "preferred_personalities": [
            "Relaxed neighbourhood pub",
            "Independent local",
            "Modern social pub"
        ]
    },
    "4": {
        "name": "Date night",
        "locked_preferences": {},
        "default_preferences": {
            "cocktails": "essential",
            "food": "essential",
            "beer_garden": "nice"
        },
        "preferred_personalities": [
            "Modern social pub",
            "Upmarket traditional pub"
        ]
    },
    "5": {
        "name": "Family meal",
        "locked_preferences": {},
        "default_preferences": {
            "food": "essential",
            "family_friendly": "essential",
            "beer_garden": "nice"
        },
        "preferred_personalities": [
            "Family-friendly country-style pub",
            "Relaxed neighbourhood pub"
        ]
    },
    "6": {
        "name": "Live music",
        "locked_preferences": {
            "live_music": "essential"
        },
        "default_preferences": {
            "cocktails": "nice",
            "late_open": "nice"
        },
        "preferred_personalities": [
            "Late-night music bar",
            "Modern social pub"
        ]
    }
}
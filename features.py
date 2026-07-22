# features.py

"""
This file contains the feature definitions used by PintFinder.

Each dictionary describes one feature that a pub may have, such as
football, food, cocktails or a beer garden.

The actual True/False values for each pub remain in pub_database.py.
This file only explains how PintFinder should refer to each feature.
"""


FEATURES = [
    {
        "database_key": "football",
        "display_name": "showing football",
        "summary_name": "Football",
        "reason": "Shows football"
    },
    {
        "database_key": "guinness",
        "display_name": "serving Guinness",
        "summary_name": "Guinness",
        "reason": "Serves Guinness"
    },
    {
        "database_key": "pool_table",
        "display_name": "having a pool table",
        "summary_name": "Pool table",
        "reason": "Has a pool table"
    },
    {
        "database_key": "beer_garden",
        "display_name": "having a beer garden",
        "summary_name": "Beer garden",
        "reason": "Has a beer garden"
    },
    {
        "database_key": "live_music",
        "display_name": "having live music",
        "summary_name": "Live music",
        "reason": "Hosts live music"
    },
    {
        "database_key": "food",
        "display_name": "serving food",
        "summary_name": "Food",
        "reason": "Serves food"
    },
    {
        "database_key": "cocktails",
        "display_name": "serving cocktails",
        "summary_name": "Cocktails",
        "reason": "Serves cocktails"
    },
    {
        "database_key": "dog_friendly",
        "display_name": "being dog-friendly",
        "summary_name": "Dog-friendly",
        "reason": "Welcomes dogs"
    },
    {
        "database_key": "family_friendly",
        "display_name": "being family-friendly",
        "summary_name": "Family-friendly",
        "reason": "Suitable for families"
    },
    {
        "database_key": "quiz_night",
        "display_name": "running a quiz night",
        "summary_name": "Quiz night",
        "reason": "Runs quiz nights"
    },
    {
        "database_key": "darts",
        "display_name": "having darts",
        "summary_name": "Darts",
        "reason": "Has darts"
    },
    {
        "database_key": "late_open",
        "display_name": "staying open late",
        "summary_name": "Late opening",
        "reason": "Stays open late"
    },
    {
        "database_key": "craft_beer",
        "display_name": "serving craft beer",
        "summary_name": "Craft beer",
        "reason": "Serves craft beer"
    }
]
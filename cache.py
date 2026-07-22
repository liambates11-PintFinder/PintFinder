# cache.py

import json
import os
from datetime import datetime, timedelta

CACHE_FILE = "storage/cache.json"
CACHE_EXPIRY_HOURS = 24


def load_cache():
    """
    Load the cache from disk.
    """

    if not os.path.exists(CACHE_FILE):
        return {}

    with open(CACHE_FILE, "r") as file:
        return json.load(file)


def save_cache(cache):
    """
    Save the cache back to disk.
    """

    with open(CACHE_FILE, "w") as file:
        json.dump(
            cache,
            file,
            indent=4,
        )


def get_cached_results(cache_key):
    """
    Return cached results if they exist and are still valid.
    """

    cache = load_cache()

    if cache_key not in cache:
        return None

    cached_time = datetime.fromisoformat(
        cache[cache_key]["timestamp"]
    )

    if datetime.now() - cached_time > timedelta(hours=CACHE_EXPIRY_HOURS):
        return None

    return cache[cache_key]["pubs"]


def save_results(cache_key, pubs):
    """
    Save search results to the cache.
    """

    cache = load_cache()

    cache[cache_key] = {
        "timestamp": datetime.now().isoformat(),
        "pubs": pubs,
    }

    save_cache(cache)
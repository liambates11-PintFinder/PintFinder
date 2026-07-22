# cache.py

import json
import os
from dataclasses import asdict
from datetime import datetime, timedelta

from models.pub import Pub


CACHE_FILE = "storage/cache.json"
CACHE_EXPIRY_HOURS = 24


def load_cache():
    """
    Load the cache from disk.

    Returns an empty dictionary if the cache file does not exist,
    is empty, or contains invalid JSON.
    """

    if not os.path.exists(CACHE_FILE):
        return {}

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            content = file.read().strip()

            if not content:
                return {}

            return json.loads(content)

    except json.JSONDecodeError:
        print("\n⚠️ Cache file was invalid and has been reset.")
        return {}


def save_cache(cache):
    """
    Save the cache dictionary to disk.
    """

    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            cache,
            file,
            indent=4,
            ensure_ascii=False,
        )


def get_cached_results(cache_key):
    """
    Return cached Pub objects if the cached entry exists
    and has not expired.
    """

    cache = load_cache()

    cached_entry = cache.get(cache_key)

    if cached_entry is None:
        return None

    timestamp = cached_entry.get("timestamp")
    cached_pubs = cached_entry.get("pubs")

    if timestamp is None or cached_pubs is None:
        return None

    try:
        cached_time = datetime.fromisoformat(timestamp)
    except ValueError:
        return None

    cache_age = datetime.now() - cached_time

    if cache_age > timedelta(hours=CACHE_EXPIRY_HOURS):
        return None

    return [
        Pub(**pub_data)
        for pub_data in cached_pubs
    ]


def save_results(cache_key, pubs):
    """
    Convert Pub objects into dictionaries and save them
    under the supplied cache key.
    """

    cache = load_cache()

    cache[cache_key] = {
        "timestamp": datetime.now().isoformat(),
        "pubs": [
            asdict(pub)
            for pub in pubs
        ],
    }

    save_cache(cache)
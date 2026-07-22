from services.cache import (
    save_results,
    get_cached_results,
)

test_pubs = [
    {"name": "The Red Lion"},
    {"name": "The White Hart"},
]

save_results("Manchester_1500", test_pubs)

cached = get_cached_results("Manchester_1500")

print(cached)
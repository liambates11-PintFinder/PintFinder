from services.location import get_coordinates
from services.places import get_nearby_pubs

location = input("Enter location: ")

lat, lng = get_coordinates(location)

pubs = get_nearby_pubs(lat, lng)

print()

print(f"Found {len(pubs)} pubs\n")

for pub in pubs:

    print(
        pub["displayName"]["text"],
        "-",
        pub.get("rating", "No rating")
    )
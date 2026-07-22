from services.location import get_coordinates

location = input("Enter a postcode or town: ")

lat, lng = get_coordinates(location)

print(lat)
print(lng)
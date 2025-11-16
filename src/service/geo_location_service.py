from geopy.geocoders import Nominatim

nominatim = Nominatim(user_agent="ecosense-ai")


class GeoLocationService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="ecosense-ai")

    def get_coordinates(self, address: str):

        location = self.geolocator.geocode(address)

        if location:
            return location.latitude, location.longitude

        return None, None

from geopy.geocoders import GoogleV3
import streamlit as st


class GeoLocationService:
    def __init__(self):
        self.geolocator = GoogleV3(st.secrets["GOOGLE_API_KEY"])

    def get_coordinates(self, address: str):

        location = self.geolocator.geocode(address)

        if location:
            return location.latitude, location.longitude

        return None, None

    def distance_between(self, coord1, coord2):
        from geopy.distance import geodesic

        return geodesic(coord1, coord2).km

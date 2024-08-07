# location_services.py

from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim
import logging

logger = logging.getLogger(__name__)

def get_user_location():
    try:
        location = streamlit_geolocation()
        if location:
            latitude = location.get("latitude")
            longitude = location.get("longitude")
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.reverse(f"{latitude},{longitude}")
            
            address = location.raw['address']
            city = address.get('city', '')
            county = address.get('county', '')
            state = address.get('state', '')
            country = address.get('country', '')
            
            location_info = f"{city}, {county}, {state}, {country}".strip(', ')
            logger.info(f"User location: {location_info}")
            return location_info
        else:
            logger.warning("No location data received.")
            return "No location data received."
    except Exception as e:
        logger.error(f"Error getting user location: {e}")
        return f"Error: {str(e)}"
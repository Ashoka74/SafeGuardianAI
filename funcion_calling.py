# location_services.py

from streamlit_geolocation import streamlit_geolocation
from geopy.geocoders import Nominatim
import logging
from googleapiclient.discovery import build 
from oauth2client import file, client, tools 

logger = logging.getLogger(__name__)

def provide_user_location():
    try:
        location = streamlit_geolocation()
        if location:
            latitude = location.get("latitude")
            longitude = location.get("longitude")
            # geolocator = Nominatim(user_agent="geoapiExercises")
            # location = geolocator.reverse(f"{latitude},{longitude}")
            
            # address = location.raw['address']
            # city = address.get('city', '')
            # county = address.get('county', '')
            # state = address.get('state', '')
            # country = address.get('country', '')
            
            # location_info = f"{city}, {county}, {state}, {country}".strip(', ')
            # logger.info(f"User location: {location_info}")
            return ' '.join([str(latitude), str(longitude)])
        else:
            logger.warning("No location data received.")
            return "No location data received."
    except Exception as e:
        logger.error(f"Error getting user location: {e}")
        return f"Error: {str(e)}"
    

def get_gmail_account() -> str:
    store = file.Storage('token.json') 
    creds = store.get() 
    service = build('gmail', 'v1', credentials=creds) 
    results = service.users().getProfile(userId='sinanrobillard@gmail.com').execute()
    return results['emailAddress']
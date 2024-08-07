
import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from audiorecorder import audiorecorder
import io
import base64
import json
import logging
from typing import Dict, Any, List
import jsonschema
import os
import datetime
time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
import google.generativeai as genai
from jsonschema import validate


from utils import GeminiConfig, schema, fix_json, fix_json_schema
from LLM.function_calling.geolocation_data import GeolocationService
from LLM.function_calling.rescue_data import get_rescue_data
from LLM.function_calling.vital_data import update_victim_json
from json_cleaner import update_victim_info

from RecueTeam import fetch_vital_data
from audio_processing import process_audio, play_audio  
from location_services import get_user_location
from api_clients import text_to_speech_elevenlabs
from state_manager import StateManager


state_manager = StateManager()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
gemini_api = os.getenv("gemini_api")
model_path = 'models/gemini-1.5-flash'  
response_type = 'application/json'
config = GeminiConfig(gemini_api, model_path, response_type)
geolocation_service = GeolocationService(os.getenv('geolocator_api'))
victim_template = fetch_vital_data.victim_template

# Streamlit setup
st.set_page_config(page_title="Natural Hazard Rescue Bot 💬", layout="wide", page_icon="⚠️")
st._config.set_option("theme.base", "dark")
st._config.set_option("theme.backgroundColor", "black")

# Initialize state
if "victim_template" not in st.session_state:
    st.session_state['victim_template'] = victim_template
if "victim_info" not in st.session_state:
    st.session_state.victim_info = victim_template
if "victim_number" not in st.session_state:
    st.session_state['victim_number'] = fetch_vital_data.set_key(st.session_state['victim_info'])

# Function calling definitions
function_calling = {
    'get_rescue_data': get_rescue_data,
    'get_location': get_user_location
}

# Gemini setup
model = genai.GenerativeModel(
    config.model_path,
    tools=list(function_calling.values()),
    system_instruction="You are a post-disaster bot. Help victims while collecting valuable data for intervention teams. Only return JSON output when calling functions.",
    safety_settings=config.safety
)
chat = model.start_chat(enable_automatic_function_calling=True)

def main():
    st.title("💬 Natural Hazard Rescue App⚠️")
    st.write("This bot is designed to help victims of natural disasters by providing support and information. It can also collect valuable data for intervention teams.")

    left, middle, right = st.columns([.5, .1, .4])

    # Chat input and display
    with left:
        chat_container(height=820)

    # Victim information display
    with right:
        display_victim_info()

def chat_container(height: int):
    with st.container(height=height, border=True):
        left_, right_ = st.columns([.8, .2])
        with right_:
            audio = audiorecorder("🎤", "stop", show_visualizer=False)
        with left_:    
            prompt = st.chat_input("Enter Query here") or process_audio(audio)
        if prompt:
            state_manager.add_message(role="user", content=prompt)
            try:
                response = generate_response(prompt)
            except Exception as e:
                logger.error(f"Error generating response: {e}")
                response = generate_manual_response(prompt)
            state_manager.add_message("assistant", response)
            try:
                play_audio(response)
            except Exception as e:
                logger.error(f"Error playing audio: {e}")
            process_json_response(response)

        state_manager.display_messages()

def display_victim_info():
    st.write("Victim Info:\n\n", st.session_state.victim_info)
    # if st.button("Send Data to Firebase"):
    try:
        fetch_vital_data.update_(st.session_state['victim_number'], st.session_state['victim_info'])
        st.success(f"timestamp:{time}\n\nvictim_id: {st.session_state['victim_number']} data sent to rescue team")
    except Exception as e:
        logger.error(f"Error sending data to Firebase: {e}")
        st.error("Failed to send data to Firebase. Please try again.")

def generate_response(user_input: str) -> str:
    response = chat.send_message(user_input)
    try:
        return response.text
    except AttributeError:
        function_calls = extract_function_calls(response)
        for function_call in function_calls:
            for function_name, function_args in function_call.items():
                return globals()[function_name](**function_args)

def generate_manual_response(user_input: str) -> str:
    response = chat.send_message(user_input)
    for part in response.candidates[0].content.parts:
        if response.candidates[0].content.parts[0].function_call:
            function_name = response.candidates[0].content.parts[0].function_call.name
            function_args = response.candidates[0].content.parts[0].function_call.args
            with st.status(f"Running function {function_name}...") as status_text:
                try:
                    function_args_dict = json.loads(function_args)
                except json.JSONDecodeError:
                    logger.error(f"Error decoding JSON: {function_args}")
                    return "Error processing function arguments."

                result = globals()[function_name](**function_args_dict)
                st.session_state.victim_info = result
                return response.text
        else:
            return response.text

def extract_function_calls(response) -> List[Dict[str, Any]]:
    function_calls = []
    if response.candidates[0].function_calls:
        for function_call in response.candidates[0].function_calls:
            function_call_dict = {function_call.name: {}}
            for key, value in function_call.args.items():
                function_call_dict[function_call.name][key] = value
            function_calls.append(function_call_dict)
    return function_calls



def process_json_response(response: str):
    if '```json' in response:
        update_victim_info(update_victim_json(new_infos=response), schema)

if __name__ == "__main__":
    main()
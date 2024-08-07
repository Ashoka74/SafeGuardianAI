# api_clients.py

import requests
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def text_to_speech_elevenlabs(text: str) -> Optional[bytes]:
    elevenlab_api = os.getenv('ELEVENLABS_API')
    if not elevenlab_api:
        logger.error("ElevenLabs API key not found in environment variables.")
        return None

    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "accept": "audio/mpeg",
        "xi-api-key": elevenlab_api,
        "Content-Type": "application/json",
    }
    data = {"text": text}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"Successfully generated speech for text: {text[:50]}...")
        return response.content
    except requests.RequestException as e:
        logger.error(f"Error in text-to-speech API call: {e}")
        return None
import os
from dotenv import load_dotenv

load_dotenv()  # Reads variables from .env into environment

API_KEY = os.getenv("CINE2NERDLE_API_KEY", "N/A")

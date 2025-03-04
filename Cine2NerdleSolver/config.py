"""
Configuration module for Cine2NerdleSolver.

Loads environment variables from a .env file and sets up the API key for TMDB.
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Reads variables from .env into environment

API_KEY = os.getenv("CINE2NERDLE_API_KEY", "N/A")

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration for the application"""
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Validate API key exists
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in .env file!")

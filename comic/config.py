"""Configuration management for Comic Strip Generator."""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""

    # API Settings
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
    GEMINI_IMAGE_MODEL = 'gemini-2.0-flash-exp'  # Model that supports image generation

    # Image Settings
    IMAGE_SIZE = os.getenv('IMAGE_SIZE', '2K')
    ASPECT_RATIO = os.getenv('ASPECT_RATIO', '16:9')
    PANEL_WIDTH = 800
    PANEL_HEIGHT = 450

    # Comic Settings
    NUM_PANELS = int(os.getenv('NUM_PANELS', 4))
    PANEL_SPACING = 20
    BORDER_WIDTH = 10

    # Style Settings
    ART_STYLE = os.getenv('ART_STYLE', 'Calvin and Hobbes')
    COLOR_MODE = os.getenv('COLOR_MODE', 'black_and_white')

    # Content Safety
    SAFETY_SETTINGS = {
        "harassment": "BLOCK_MEDIUM_AND_ABOVE",
        "hate_speech": "BLOCK_MEDIUM_AND_ABOVE",
        "sexually_explicit": "BLOCK_LOW_AND_ABOVE",
        "dangerous_content": "BLOCK_MEDIUM_AND_ABOVE"
    }

    # Output Settings
    BASE_DIR = Path(__file__).parent
    OUTPUT_DIR = BASE_DIR / os.getenv('OUTPUT_DIR', 'output')
    OUTPUT_FORMAT = os.getenv('OUTPUT_FORMAT', 'PNG')
    CHARACTER_LIBRARY_PATH = BASE_DIR / 'character_library.json'

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not set. Please configure .env file.")

        # Ensure output directory exists
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        return True

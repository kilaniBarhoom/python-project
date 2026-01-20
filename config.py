"""
Application configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'smart_records_secret_key_2024')
    MONGODB_URI = os.getenv('MONGODB_URI')
    DEBUG = True


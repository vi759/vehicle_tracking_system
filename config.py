import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""

    # Database Configuration
    # FIX: os.getenv() first arg must be the ENV VARIABLE NAME, not the value.
    # Previously: os.getenv('127.0.0.1', 'localhost') — this never reads from .env
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'vehicle_tracking')

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'

    # Camera Configuration
    CAMERA_SOURCE = os.getenv('CAMERA_SOURCE', 'http://192.168.1.5:4747/video')
    FALLBACK_CAMERA = int(os.getenv('FALLBACK_CAMERA', '0'))

    # Upload Configuration
    UPLOAD_FOLDER = 'static/images'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

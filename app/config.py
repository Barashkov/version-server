import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Authentication
    AUTH_USERNAME = os.getenv('AUTH_USERNAME', 'admin')
    AUTH_PASSWORD = os.getenv('AUTH_PASSWORD', 'admin1admin')
    
    # Data Storage
    DATA_FILE = os.getenv('DATA_FILE', 'services.json')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        required_vars = ['AUTH_USERNAME', 'AUTH_PASSWORD']
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")

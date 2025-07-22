"""
Configuration management for the climate data application.
Supports environment-specific settings for development and AWS deployment.
"""

import os
from pathlib import Path
from typing import Optional

class Config:
    """Base configuration class."""
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///climate_data.db')
    
    # Data Processing Configuration
    DATA_DIR = Path(os.getenv('DATA_DIR', 'data'))
    RAW_DATA_DIR = DATA_DIR / 'raw'
    CLEAN_DATA_DIR = DATA_DIR / 'clean'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    
    @classmethod
    def init_directories(cls):
        """Initialize required directories."""
        cls.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.CLEAN_DATA_DIR.mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_URL = 'sqlite:///climate_data_dev.db'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Use environment variables for sensitive production settings
    DATABASE_URL = os.getenv('DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    @classmethod
    def validate_production_config(cls):
        """Validate that required production settings are present."""
        required_vars = ['SECRET_KEY']
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required production environment variables: {', '.join(missing)}")

class TestConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'  # In-memory database for tests

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}

def get_config(env: Optional[str] = None) -> Config:
    """Get configuration for the specified environment."""
    if env is None:
        env = os.getenv('FLASK_ENV', 'default')
    
    config_class = config.get(env, DevelopmentConfig)
    
    # Validate production config if in production
    if env == 'production':
        config_class.validate_production_config()
    
    # Initialize directories
    config_class.init_directories()
    
    return config_class
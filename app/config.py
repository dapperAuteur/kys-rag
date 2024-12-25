from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional

class Settings(BaseSettings):
    """Application settings with environment variable support.
    
    This class manages all application settings with proper defaults
    and environment variable overrides. It includes comprehensive
    settings for MongoDB Atlas, model configuration, and processing
    parameters.
    """
    
    # MongoDB connection settings
    MONGODB_ATLAS_URI: str = "mongodb+srv://username:password@cluster.mongodb.net/"
    MONGODB_LOCAL_URI: str = "mongodb://localhost:27017/"
    DATABASE_NAME: str = "science_decoder"
    
    # MongoDB Atlas search settings
    VECTOR_DIMENSIONS: int = 768  # SciBERT embedding dimensions
    VECTOR_SIMILARITY: str = "cosine"
    
    # Model settings
    MODEL_NAME: str = "allenai/scibert_scivocab_uncased"
    MODEL_MAX_LENGTH: int = 512
    
    # Text processing settings
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # API settings
    API_TITLE: str = "Science Decoder API"
    API_DESCRIPTION: str = "API for analyzing scientific papers and articles"
    API_VERSION: str = "2.0.0"
    
    # Application settings
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    
    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Create and cache settings instance for better performance.
    
    This function creates a singleton instance of the Settings class,
    caching it for repeated use. This improves performance by avoiding
    repeated environment variable lookups.
    
    Returns:
        Settings: Cached application settings instance.
    """
    return Settings()

# Create settings instance for use in other modules
settings = get_settings()
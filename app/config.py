from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with environment variable support and type validation.
    
    This class manages all application settings, with special handling for MongoDB
    connections to support both Atlas and local deployments.
    """
    
    # MongoDB connection settings
    MONGODB_ATLAS_URI: str = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/"
    MONGODB_LOCAL_URI: str = "mongodb://localhost:27017/"
    DATABASE_NAME: str = "science_decoder"
    
    # Vector search settings
    VECTOR_DIMENSIONS: int = 768  # SciBERT embedding dimensions
    VECTOR_SIMILARITY: str = "cosine"  # Similarity metric for vector search
    
    # Model settings
    MODEL_NAME: str = "allenai/scibert_scivocab_uncased"
    
    # Text processing settings
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # Application settings
    LOG_LEVEL: str = "INFO"
    
    class Config:
        """Settings configuration with environment variable support"""
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Create and cache settings instance for better performance.
    
    Returns:
        Settings: Cached application settings instance.
    """
    return Settings()
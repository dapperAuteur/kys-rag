from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    MONGODB_ATLAS_URI: str = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/"
    MONGODB_LOCAL_URI: str = "mongodb://localhost:27017/"
    DATABASE_NAME: str = "science_decoder"
    MODEL_NAME: str = "allenai/scibert_scivocab_uncased"
    VECTOR_DIMENSIONS: int = 768
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Create and cache settings instance"""
    return Settings()
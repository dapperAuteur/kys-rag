from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Literal
import logging

class Settings(BaseSettings):
    """Application settings with validation."""
    
    # MongoDB settings
    MONGODB_ATLAS_URI: str = Field(
        ...,  # ... means this field is required
        description="MongoDB Atlas connection string"
    )
    DATABASE_NAME: str = Field(
        default="science_decoder",
        description="MongoDB database name"
    )
    
    # Vector search settings
    VECTOR_DIMENSIONS: int = Field(
        default=768, 
        description="SciBERT embedding dimensions"
    )
    VECTOR_SIMILARITY: Literal["cosine", "euclidean", "dot_product"] = Field(
        default="cosine",
        description="Vector similarity metric"
    )
    
    # Model settings
    MODEL_NAME: str = Field(
        default="allenai/scibert_scivocab_uncased",
        description="Hugging Face model name"
    )
    
    # Text processing settings
    CHUNK_SIZE: int = Field(
        default=512, 
        description="Text chunk size"
    )
    CHUNK_OVERLAP: int = Field(
        default=50, 
        description="Overlap between chunks"
    )
    
    # Application settings
    LOG_LEVEL: str = Field(
        default="INFO", 
        description="Logging level"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Create and cache settings instance."""
    try:
        settings = Settings()
        logging.info("Settings loaded successfully")
        return settings
    except Exception as e:
        logging.error(f"Failed to load settings: {e}")
        raise
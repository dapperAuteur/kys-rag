from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Literal
import logging
import os

class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Environment
    ENV: str = Field(default="dev", description="Environment (dev/test/prod)")
    
    # MongoDB settings
    MONGODB_ATLAS_URI: str = Field(
        ...,  # ... means this field is required
        description="MongoDB Atlas connection string"
    )
    DATABASE_NAME: str = Field(
        default="science_decoder",
        description="MongoDB database name"
    )
    
    @property
    def TEST_DATABASE_NAME(self) -> str:
        """Get test database name."""
        return f"{self.DATABASE_NAME}_test"
    
    @property
    def ACTIVE_DATABASE_NAME(self) -> str:
        """Get active database name based on environment."""
        return self.TEST_DATABASE_NAME if self.ENV == "test" else self.DATABASE_NAME
    
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
        logging.info(f"Settings loaded successfully for environment: {settings.ENV}")
        return settings
    except Exception as e:
        logging.error(f"Failed to load settings: {e}")
        raise
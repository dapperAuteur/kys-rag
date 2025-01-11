from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Literal
import logging
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Environment
    ENV: str = Field(default="dev", description="Environment (dev/test/prod)")
    
    # Base Paths
    APP_DIR: Path = Field(
        default=Path(__file__).parent.parent,
        description="Application root directory"
    )
    PROJECT_ROOT: Path = Field(
        default=Path(__file__).parent.parent.parent,
        description="Project root directory"
    )
    CACHE_DIR: Path = Field(
        default=Path(__file__).parent.parent / "cache",
        description="Base cache directory"
    )
    MODEL_CACHE_DIR: Path = Field(
        default=Path(__file__).parent.parent / "cache" / "models",
        description="Model cache directory"
    )
    
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
    
    # Collection names
    SCIENTIFIC_STUDIES_COLLECTION: str = Field(
        default="scientific_studies",
        description="Collection name for scientific studies"
    )
    ARTICLES_COLLECTION: str = Field(
        default="articles",
        description="Collection name for news articles"
    )
    CHAT_HISTORY_COLLECTION: str = Field(
        default="chat_history",
        description="Collection name for chat history"
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
    
    # Claims verification settings
    MIN_CLAIM_CONFIDENCE: float = Field(
        default=0.7,
        description="Minimum confidence score for claim verification"
    )
    
    # Search settings
    DEFAULT_SEARCH_LIMIT: int = Field(
        default=10,
        description="Default number of search results"
    )
    MIN_SIMILARITY_SCORE: float = Field(
        default=0.5,
        description="Minimum similarity score for search results"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Ensure cache directories exist
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        # Set HuggingFace cache directory environment variable
        os.environ["TRANSFORMERS_CACHE"] = str(self.MODEL_CACHE_DIR)
        
        # Log cache directory locations in debug mode
        logging.debug(f"Cache directory: {self.CACHE_DIR}")
        logging.debug(f"Model cache directory: {self.MODEL_CACHE_DIR}")

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
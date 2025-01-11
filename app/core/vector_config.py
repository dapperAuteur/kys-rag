from pydantic_settings import BaseSettings
from functools import lru_cache

class VectorServiceSettings(BaseSettings):
    """Configuration settings for the Vector Service.
    
    These settings control how the Vector Service processes and manages text embeddings.
    """
    
    # Model settings
    MODEL_NAME: str = "allenai/scibert_scivocab_uncased"
    MAX_CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # Processing settings
    BATCH_SIZE: int = 32
    USE_GPU: bool = True
    
    # Similarity settings
    MIN_SIMILARITY_SCORE: float = 0.5
    
    # Cache settings
    CACHE_SIZE: int = 1000
    
    class Config:
        env_prefix = "VECTOR_"
        case_sensitive = True

@lru_cache()
def get_vector_settings() -> VectorServiceSettings:
    """Get cached vector service settings.
    
    Returns:
        VectorServiceSettings instance with current configuration
    """
    return VectorServiceSettings()
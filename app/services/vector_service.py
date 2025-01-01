from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
from app.core.config import get_settings
import numpy as np

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class ProcessingMetrics:
    """Tracks metrics for text processing operations.
    
    Attributes:
        chunk_count: Number of chunks the text was split into
        processing_time: Time taken to process in seconds
        input_length: Length of input text in characters
        success: Whether processing completed successfully
        error_message: Error message if processing failed
    """
    chunk_count: int
    processing_time: float
    input_length: int
    success: bool
    error_message: str = ""

class VectorService:
    """Service for converting text into vector embeddings.
    
    This service handles the conversion of text into numerical vectors that
    capture semantic meaning, making it possible to compare and analyze
    text content programmatically.
    """
    
    def __init__(self):
        """Initialize the vector service with required models and settings."""
        logger.info("Initializing VectorService")
        self.settings = get_settings()
        
        # Load language models
        try:
            logger.info(f"Loading model: {self.settings.MODEL_NAME}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.settings.MODEL_NAME)
            self.model = AutoModel.from_pretrained(self.settings.MODEL_NAME)
            logger.info("Models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            raise
        
        # Initialize metrics storage
        self.metrics: Dict[str, ProcessingMetrics] = {}
        
        # Set device (GPU if available)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        logger.info(f"Using device: {self.device}")

    async def _preprocess_text(self, text: str) -> str:
        """Clean and normalize text before processing.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned and normalized text
        """
        logger.debug(f"Preprocessing text of length: {len(text)}")
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Normalize line endings and tabs
        text = text.replace("\n", " ").replace("\t", " ")
        
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        
        logger.debug(f"Preprocessing complete. New length: {len(text)}")
        return text

    def _chunk_text(self, text: str, chunk_size: int = 512) -> List[str]:
        """Split text into overlapping chunks for processing.
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        overlap = min(50, chunk_size // 10)  # 10% overlap, max 50 words
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = words[i:i + chunk_size]
            chunk_text = " ".join(chunk)
            chunks.append(chunk_text)
            
        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks

    async def _generate_chunk_embedding(self, chunk: str) -> torch.Tensor:
        """Generate embedding for a single chunk of text.
        
        Args:
            chunk: Text chunk to process
            
        Returns:
            Tensor containing chunk embedding
        """
        try:
            # Prepare input
            inputs = self.tokenizer(
                chunk,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512
            )
            
            # Move inputs to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Generate embedding
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)
                
            # Normalize embedding
            normalized = torch.nn.functional.normalize(embeddings)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error generating chunk embedding: {e}")
            raise

    def _combine_embeddings(self, embeddings: List[torch.Tensor]) -> List[float]:
        """Combine multiple chunk embeddings into a single embedding.
        
        Args:
            embeddings: List of chunk embeddings
            
        Returns:
            Combined embedding as list of floats
        """
        try:
            # Stack embeddings
            stacked = torch.stack(embeddings)
            
            # Average across chunks
            averaged = torch.mean(stacked, dim=0)
            
            # Convert to list
            return averaged.squeeze().cpu().tolist()
            
        except Exception as e:
            logger.error(f"Error combining embeddings: {e}")
            raise

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate vector embedding for input text.
        
        This is the main public method for converting text to vectors.
        
        Args:
            text: Input text to vectorize
            
        Returns:
            Vector embedding as list of floats, or None if processing fails
        """
        start_time = datetime.now()
        text_id = text[:50]  # Use first 50 chars as ID
        
        try:
            # Preprocess text
            text = await self._preprocess_text(text)
            
            # Split into chunks
            chunks = self._chunk_text(text)
            
            # Process each chunk
            embeddings = []
            for chunk in chunks:
                embedding = await self._generate_chunk_embedding(chunk)
                embeddings.append(embedding)
            
            # Combine chunk embeddings
            final_embedding = self._combine_embeddings(embeddings)
            
            # Record metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics[text_id] = ProcessingMetrics(
                chunk_count=len(chunks),
                processing_time=processing_time,
                input_length=len(text),
                success=True
            )
            
            return final_embedding
            
        except Exception as e:
            # Record failure metrics
            self.metrics[text_id] = ProcessingMetrics(
                chunk_count=0,
                processing_time=0,
                input_length=len(text),
                success=False,
                error_message=str(e)
            )
            logger.error(f"Failed to generate embedding: {e}")
            return None

    async def get_processing_metrics(self) -> Dict[str, ProcessingMetrics]:
        """Retrieve processing metrics for monitoring and debugging.
        
        Returns:
            Dictionary of processing metrics keyed by text ID
        """
        return self.metrics

    async def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            # Ensure result is between 0 and 1
            return float(max(0.0, min(1.0, similarity)))
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

# Create singleton instance
vector_service = VectorService()

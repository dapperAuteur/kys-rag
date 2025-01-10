# app/migrations/vector_migrations.py

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from .base import BaseMigration
from app.core.database import Collection
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)

class UpdateArticleVectors(BaseMigration):
    """Migration to update article vectors using new Vector Service."""
    
    def __init__(self):
        super().__init__(Collection.ARTICLES)
    
    async def should_process_document(self, document: Dict[str, Any]) -> bool:
        """Check if article needs vector update."""
        # Process if vector is missing or if we're forcing updates
        return (
            'vector' not in document or
            document.get('vector') is None or
            len(document.get('vector', [])) == 0
        )
    
    async def process_document(self, document: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process article document to update its vector."""
        try:
            # Generate new vector
            text = document.get('text', '')
            if not text:
                logger.warning(f"No text found in document {document.get('_id')}")
                return None
                
            new_vector = await vector_service.generate_embedding(text)
            if not new_vector:
                logger.error(f"Failed to generate vector for article {document.get('_id')}")
                return None
            
            # Update document with new vector
            document['vector'] = new_vector
            document['updated_at'] = datetime.utcnow()
            
            return document
            
        except Exception as e:
            logger.error(f"Error processing article {document.get('_id')}: {e}")
            return None

class UpdateStudyVectors(BaseMigration):
    """Migration to update scientific study vectors using new Vector Service."""
    
    def __init__(self):
        super().__init__(Collection.SCIENTIFIC_STUDIES)
    
    async def should_process_document(self, document: Dict[str, Any]) -> bool:
        """Check if study needs vector update."""
        return (
            'vector' not in document or
            document.get('vector') is None or
            len(document.get('vector', [])) == 0
        )
    
    async def process_document(self, document: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process study document to update its vector."""
        try:
            # Combine relevant text fields for vectorization
            text_parts = [
                document.get('title', ''),
                document.get('abstract', ''),
                document.get('text', '')
            ]
            text = ' '.join(filter(None, text_parts))
            
            if not text:
                logger.warning(f"No text found in study {document.get('_id')}")
                return None
            
            # Generate new vector
            new_vector = await vector_service.generate_embedding(text)
            if not new_vector:
                logger.error(f"Failed to generate vector for study {document.get('_id')}")
                return None
            
            # Update document with new vector
            document['vector'] = new_vector
            document['updated_at'] = datetime.utcnow()
            
            return document
            
        except Exception as e:
            logger.error(f"Error processing study {document.get('_id')}: {e}")
            return None
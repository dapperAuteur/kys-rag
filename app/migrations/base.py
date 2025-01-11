# app/migrations/base.py

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorCollection
from app.core.database import database
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)

class MigrationMetadata(BaseModel):
    """Tracks the status and details of migrations."""
    name: str
    timestamp: datetime
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    total_records: int = 0
    processed_records: int = 0
    failed_records: List[str] = []
    error_messages: Dict[str, str] = {}
    
class BaseMigration:
    """Base class for database migrations."""
    
    def __init__(self, collection_name: str):
        """Initialize migration with collection name."""
        self.collection_name = collection_name
        self.metadata = MigrationMetadata(
            name=self.__class__.__name__,
            timestamp=datetime.utcnow(),
            status='pending'
        )
    
    async def get_collection(self) -> AsyncIOMotorCollection:
        """Get the database collection."""
        return await database.get_collection(self.collection_name)
    
    async def count_documents(self) -> int:
        """Count total documents to be processed."""
        collection = await self.get_collection()
        return await collection.count_documents({})
    
    async def update_metadata(self) -> None:
        """Update migration metadata in database."""
        migrations_collection = await database.get_collection('migrations')
        await migrations_collection.update_one(
            {'name': self.metadata.name},
            {'$set': self.metadata.model_dump()},
            upsert=True
        )
    
    async def log_progress(self, current: int, total: int) -> None:
        """Log migration progress."""
        progress = (current / total) * 100 if total > 0 else 0
        logger.info(f"Migration progress: {progress:.2f}% ({current}/{total})")
        
        # Update metadata
        self.metadata.processed_records = current
        self.metadata.total_records = total
        await self.update_metadata()
    
    async def process_document(self, document: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single document. Override in subclasses."""
        raise NotImplementedError
    
    async def should_process_document(self, document: Dict[str, Any]) -> bool:
        """Determine if document needs processing. Override in subclasses."""
        raise NotImplementedError
    
    async def run(self, batch_size: int = 100) -> None:
        """Run the migration."""
        try:
            logger.info(f"Starting migration: {self.metadata.name}")
            self.metadata.status = 'in_progress'
            await self.update_metadata()
            
            collection = await self.get_collection()
            total_docs = await self.count_documents()
            processed = 0
            
            cursor = collection.find({})
            batch = []
            
            async for document in cursor:
                if await self.should_process_document(document):
                    try:
                        processed_doc = await self.process_document(document)
                        if processed_doc:
                            batch.append(processed_doc)
                    except Exception as e:
                        logger.error(f"Error processing document {document.get('_id')}: {e}")
                        self.metadata.failed_records.append(str(document.get('_id')))
                        self.metadata.error_messages[str(document.get('_id'))] = str(e)
                
                if len(batch) >= batch_size:
                    # Bulk update processed documents
                    await self._update_batch(batch)
                    batch = []
                
                processed += 1
                if processed % 10 == 0:  # Log progress every 10 documents
                    await self.log_progress(processed, total_docs)
            
            # Process remaining batch
            if batch:
                await self._update_batch(batch)
            
            self.metadata.status = 'completed'
            logger.info(f"Migration completed: {self.metadata.name}")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            self.metadata.status = 'failed'
            self.metadata.error_messages['migration_error'] = str(e)
            
        finally:
            await self.update_metadata()
    
    async def _update_batch(self, batch: List[Dict[str, Any]]) -> None:
        """Update a batch of documents in the database."""
        if not batch:
            return
            
        collection = await self.get_collection()
        operations = []
        
        for doc in batch:
            doc_id = doc.pop('_id')
            operations.append(
                {
                    'update_one': {
                        'filter': {'_id': doc_id},
                        'update': {'$set': doc}
                    }
                }
            )
        
        if operations:
            try:
                await collection.bulk_write(operations, ordered=False)
            except Exception as e:
                logger.error(f"Error updating batch: {e}")
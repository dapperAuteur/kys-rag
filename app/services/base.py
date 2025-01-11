from typing import List, Optional, TypeVar, Generic, Any
from datetime import datetime
import logging
from app.core.database import database, Collection
from app.models.models import BaseDocument
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from .vector_service import vector_service  # Import our new VectorService

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseDocument)

class BaseService(Generic[T]):
    """Base service with common functionality for all content types."""
    
    def __init__(self, collection: Collection, model_class: type[T]):
        """Initialize the service with specific collection and model."""
        self.collection_name = collection
        self.model_class = model_class
        self.settings = database.settings
    
    async def get_collection(self) -> AsyncIOMotorCollection:
        """Get the database collection for this service."""
        logger.info(f"Getting collection: {self.collection_name}")
        return await database.get_collection(self.collection_name)

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate vector embedding for text using VectorService."""
        try:
            logger.info(f"Generating embedding for text of length: {len(text)}")
            return await vector_service.generate_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    async def create(self, item: T) -> str:
        """Create a new item with vector embedding."""
        try:
            logger.info(f"Creating new {self.collection_name} item")
            
            # Generate vector embedding if not provided
            if not item.vector and hasattr(item, 'text'):
                item.vector = await self.generate_embedding(item.text)
                if not item.vector:
                    raise ValueError("Failed to generate vector embedding")
            
            # Set timestamps
            item.created_at = datetime.utcnow()
            item.updated_at = datetime.utcnow()
            
            # Convert to dict and remove None values
            document = item.model_dump(by_alias=True, exclude_none=True)
            
            # Remove id if it's None
            if "_id" in document and document["_id"] is None:
                del document["_id"]
            
            # Get collection and insert document
            coll = await self.get_collection()
            result = await coll.insert_one(document)
            
            logger.info(f"Created new {self.collection_name} with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating {self.collection_name}: {e}")
            raise

    async def get_by_id(self, item_id: str) -> Optional[T]:
        """Retrieve an item by its ID."""
        try:
            coll = await database.get_collection(self.collection_name)
            document = await coll.find_one({"_id": ObjectId(item_id)})
            if document:
                return self.model_class(**document)
            return None
        except Exception as e:
            logger.error(f"Error retrieving {self.collection_name}: {e}")
            raise

    async def update(self, item_id: str, item: T) -> bool:
        """Update an existing item."""
        try:
            # Update vector if text has changed
            if hasattr(item, 'text'):
                item.vector = await self.generate_embedding(item.text)
            
            item.updated_at = datetime.utcnow()
            update_data = item.model_dump(by_alias=True, exclude_none=True)
            
            # Remove id from update data
            if "_id" in update_data:
                del update_data["_id"]
            
            coll = await database.get_collection(self.collection_name)
            result = await coll.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Updated {self.collection_name} with ID: {item_id}")
            return success
        except Exception as e:
            logger.error(f"Error updating {self.collection_name}: {e}")
            raise

    async def delete(self, item_id: str) -> bool:
        """Delete an item by its ID."""
        try:
            coll = await database.get_collection(self.collection_name)
            result = await coll.delete_one({"_id": ObjectId(item_id)})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted {self.collection_name} with ID: {item_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting {self.collection_name}: {e}")
            raise

    async def search_similar(
        self,
        query_text: str,
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[dict]:
        """Search for similar items using vector similarity."""
        try:
            # Generate query vector
            query_vector = await self.generate_embedding(query_text)
            if not query_vector:
                raise ValueError("Failed to generate query vector")
            
            coll = await database.get_collection(self.collection_name)
            
            # Use vector_service to calculate similarities
            pipeline = [
                {
                    "$addFields": {
                        "similarity": {
                            "$let": {
                                "vars": {
                                    "dotProduct": {
                                        "$reduce": {
                                            "input": {"$zip": {"inputs": ["$vector", query_vector]}},
                                            "initialValue": 0.0,
                                            "in": {
                                                "$add": [
                                                    "$$value",
                                                    {"$multiply": [
                                                        {"$arrayElemAt": ["$$this", 0]},
                                                        {"$arrayElemAt": ["$$this", 1]}
                                                    ]}
                                                ]
                                            }
                                        }
                                    }
                                },
                                "in": {
                                    "$min": [1.0, {"$max": [0.0, "$$dotProduct"]}]
                                }
                            }
                        }
                    }
                },
                {"$match": {"similarity": {"$gte": min_score}}},
                {"$sort": {"similarity": -1}},
                {"$limit": limit}
            ]
            
            results = await coll.aggregate(pipeline).to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Error searching {self.collection_name}: {e}")
            raise
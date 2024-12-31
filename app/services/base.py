from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Optional, TypeVar, Generic, Any
from datetime import datetime
import logging
from app.core.database import database, Collection
from app.models.models import BaseDocument
from bson import ObjectId

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseDocument)

class BaseService(Generic[T]):
    """Base service with common functionality for all content types."""
    
    def __init__(self, collection: Collection, model_class: type[T]):
        """Initialize the service with specific collection and model."""
        self.collection = collection
        self.model_class = model_class
        self.settings = database.settings
        
        # Initialize ML models
        self.tokenizer = AutoTokenizer.from_pretrained(self.settings.MODEL_NAME)
        self.model = AutoModel.from_pretrained(self.settings.MODEL_NAME)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for text using SciBERT."""
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=self.settings.CHUNK_SIZE,
                padding=True
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
                # Normalize the embedding
                normalized = embedding / torch.norm(embedding)
                return normalized.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def create(self, item: T) -> str:
        """Create a new item with vector embedding."""
        try:
            # Generate vector embedding if not provided
            if not item.vector:
                item.vector = await self.generate_embedding(item.text)
            
            # Set timestamps
            item.created_at = datetime.utcnow()
            item.updated_at = datetime.utcnow()
            
            # Convert to dict and remove None values
            document = item.model_dump(by_alias=True, exclude_none=True)
            
            # Remove id if it's None
            if "_id" in document and document["_id"] is None:
                del document["_id"]
            
            # Get collection and insert document
            coll = await database.get_collection(self.collection)
            result = await coll.insert_one(document)
            
            logger.info(f"Created new {self.collection.value} with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating {self.collection.value}: {e}")
            raise

    async def get_by_id(self, item_id: str) -> Optional[T]:
        """Retrieve an item by its ID."""
        try:
            coll = await database.get_collection(self.collection)
            document = await coll.find_one({"_id": ObjectId(item_id)})
            if document:
                return self.model_class(**document)
            return None
        except Exception as e:
            logger.error(f"Error retrieving {self.collection.value}: {e}")
            raise

    async def update(self, item_id: str, item: T) -> bool:
        """Update an existing item."""
        try:
            item.updated_at = datetime.utcnow()
            update_data = item.model_dump(by_alias=True, exclude_none=True)
            
            # Remove id from update data
            if "_id" in update_data:
                del update_data["_id"]
            
            coll = await database.get_collection(self.collection)
            result = await coll.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": update_data}
            )
            
            success = result.modified_count > 0
            if success:
                logger.info(f"Updated {self.collection.value} with ID: {item_id}")
            return success
        except Exception as e:
            logger.error(f"Error updating {self.collection.value}: {e}")
            raise

    async def delete(self, item_id: str) -> bool:
        """Delete an item by its ID."""
        try:
            coll = await database.get_collection(self.collection)
            result = await coll.delete_one({"_id": ObjectId(item_id)})
            
            success = result.deleted_count > 0
            if success:
                logger.info(f"Deleted {self.collection.value} with ID: {item_id}")
            return success
        except Exception as e:
            logger.error(f"Error deleting {self.collection.value}: {e}")
            raise

    async def search_similar(
        self,
        query_text: str,
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[dict]:
        """Search for similar items using vector similarity."""
        try:
            query_vector = await self.generate_embedding(query_text)
            
            coll = await database.get_collection(self.collection)
            
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
            logger.error(f"Error searching {self.collection.value}: {e}")
            raise
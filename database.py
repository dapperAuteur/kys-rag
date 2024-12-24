from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, List
import logging
from config import get_settings
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations with metadata support"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.settings = get_settings()
        self.vector_search_enabled = False
    
    async def connect(self) -> None:
        """Connect to MongoDB Atlas with local fallback"""
        try:
            # First try Atlas connection
            logger.info("Attempting to connect to MongoDB Atlas...")
            self.client = AsyncIOMotorClient(self.settings.MONGODB_ATLAS_URI)
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
        except Exception as e:
            logger.warning(f"Failed to connect to Atlas: {e}")
            try:
                # Fallback to local MongoDB
                logger.info("Attempting to connect to local MongoDB...")
                self.client = AsyncIOMotorClient(self.settings.MONGODB_LOCAL_URI)
                await self.client.admin.command('ping')
                logger.info("Successfully connected to local MongoDB")
            except Exception as e:
                logger.error(f"Failed to connect to local MongoDB: {e}")
                raise ConnectionError("Could not connect to any MongoDB instance")
        
        self.db = self.client[self.settings.DATABASE_NAME]
        
        # Setup indexes for vector search and metadata
        await self.setup_indexes()

    async def setup_indexes(self) -> None:
        """Create necessary database indexes for vectors and metadata"""
        try:
            # Vector search index setup
            try:
                logger.info("Attempting to create vector search index...")
                await self.db.studies.create_index(
                    [("vector", "vector")],
                    name="vector_index",
                    vectorSearchOptions={
                        "numDimensions": self.settings.VECTOR_DIMENSIONS,
                        "similarity": "cosine"
                    }
                )
                self.vector_search_enabled = True
                logger.info("Vector search index created successfully")
            except Exception as e:
                logger.warning(f"Vector search not available: {e}")
                logger.info("Creating regular indexes for basic vector storage...")
                await self.db.studies.create_index("vector")
                self.vector_search_enabled = False
            
            # Create text search index for metadata
            await self.db.studies.create_index(
                [
                    ("title", "text"),
                    ("text", "text"),
                    ("topic", "text"),
                    ("keywords", "text")
                ],
                name="text_search_index"
            )
            
            # Create indexes for common metadata queries
            await self.db.studies.create_index([("publication_date", -1)])
            await self.db.studies.create_index([("citation_count", -1)])
            await self.db.studies.create_index([("doi", 1)], unique=True, sparse=True)
            await self.db.studies.create_index([("created_at", -1)])
            await self.db.studies.create_index([("discipline", 1)])
            await self.db.studies.create_index([("authors.name", 1)])
            
            logger.info("All indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise

    async def vector_similarity_search(
        self,
        query_vector: List[float],
        limit: int = 5,
        metadata_filters: Optional[dict] = None
    ) -> List[dict]:
        """
        Perform vector similarity search with metadata filtering
        """
        try:
            pipeline = []
            
            if self.vector_search_enabled:
                # Use native vector search if available
                pipeline.append({
                    "$search": {
                        "index": "vector_index",
                        "knnBeta": {
                            "vector": query_vector,
                            "path": "vector",
                            "k": limit * 2  # Get more results for filtering
                        }
                    }
                })
            else:
                # Fallback: Manual similarity calculation
                pipeline.extend([
                    {
                        "$project": {
                            "vector": 1,
                            "title": 1,
                            "text": 1,
                            "topic": 1,
                            "discipline": 1,
                            "authors": 1,
                            "publication_date": 1,
                            "keywords": 1,
                            "citation_count": 1,
                            "doi": 1,
                            "created_at": 1,
                            "similarity": {
                                "$function": {
                                    "body": """function(a, b) {
                                        return Array.zip(a, b).reduce((sum, pair) => 
                                            sum + pair[0] * pair[1], 0) /
                                            (Math.sqrt(a.reduce((sum, val) => 
                                                sum + val * val, 0)) *
                                            Math.sqrt(b.reduce((sum, val) => 
                                                sum + val * val, 0)));
                                    }""",
                                    "args": ["$vector", query_vector],
                                    "lang": "js"
                                }
                            }
                        }
                    },
                    {"$sort": {"similarity": -1}}
                ])
            
            # Apply metadata filters if provided
            if metadata_filters:
                pipeline.append({"$match": metadata_filters})
            
            # Final stages
            pipeline.extend([
                {"$limit": limit},
                {
                    "$project": {
                        "vector": 0,
                        "score": {
                            "$cond": {
                                "if": self.vector_search_enabled,
                                "then": {"$meta": "searchScore"},
                                "else": "$similarity"
                            }
                        }
                    }
                }
            ])
            
            results = await self.db.studies.aggregate(pipeline).to_list(length=limit)
            return results
            
        except Exception as e:
            logger.error(f"Error in vector similarity search: {e}")
            raise

    async def update_citation_count(self, study_id: str, new_count: int) -> None:
        """Update the citation count for a study"""
        try:
            await self.db.studies.update_one(
                {"_id": ObjectId(study_id)},
                {
                    "$set": {
                        "citation_count": new_count,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error updating citation count: {e}")
            raise

    async def close(self) -> None:
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

database = DatabaseManager()
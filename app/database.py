from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
from config import get_settings
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
from bson import ObjectId

# Configure logging for our database operations

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations with metadata support"""
    
    def __init__(self):
        """Initialize database manager with settings and connection state."""
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None
        self.settings = get_settings()
        self.vector_search_enabled = False

        logger.info("DatabaseManager initialized with settings")
    
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
            await self._setup_vector_index()
            await self._setup_text_index()
            await self._setup_metadata_indexes()
            
            logger.info("All indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise

    async def _setup_vector_index(self) -> None:
        """Setup vector search index with fallback"""
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
        except OperationFailure as e:
            if "disallowed in this Atlas tier" in str(e):
                logger.warning("Vector search not available in current Atlas tier")
                await self._setup_fallback_vector_index()
            else:
                raise

    async def _setup_fallback_vector_index(self) -> None:
      """Setup basic vector index when vector search is not available"""
      try:
          # Check for existing vector index first
          existing_indexes = await self.db.studies.list_indexes().to_list(None)
          has_vector_index = any(
              'vector' in idx.get('name', '') for idx in existing_indexes
          )
          
          if has_vector_index:
              logger.info("Basic vector index already exists, skipping creation")
              self.vector_search_enabled = False
              return
              
          logger.info("Creating regular index for basic vector storage...")
          await self.db.studies.create_index([("vector", 1)], name="basic_vector_index")
          self.vector_search_enabled = False
          logger.info("Basic vector index created successfully")
      except Exception as e:
          logger.error(f"Failed to create basic vector index: {e}")
          # Don't raise here - just log the error since we can still operate with an existing index
          self.vector_search_enabled = False

    async def _setup_text_index(self) -> None:
        """Setup text search index with conflict handling"""
        try:
            # Check existing indexes
            existing_indexes = await self.db.studies.list_indexes().to_list(None)
            has_text_index = any(
                'text' in idx.get('name', '') or 
                idx.get('textIndexVersion') is not None 
                for idx in existing_indexes
            )
            
            if has_text_index:
                logger.info("Text index already exists, skipping creation")
                return
            
            await self.db.studies.create_index(
                [
                    ("title", "text"),
                    ("text", "text"),
                    ("topic", "text"),
                    ("keywords", "text")
                ],
                name="text_search_index",
                weights={
                    "title": 10,
                    "keywords": 5,
                    "topic": 3,
                    "text": 1
                }
            )
            logger.info("Text search index created successfully")
        except OperationFailure as e:
            if "equivalent index already exists" in str(e):
                logger.info("Equivalent text index already exists, using existing index")
            else:
                raise

    async def _setup_metadata_indexes(self) -> None:
        """Setup indexes for metadata fields"""
        try:
            index_specs = [
                ([("publication_date", -1)], {}),
                ([("citation_count", -1)], {}),
                ([("doi", 1)], {"unique": True, "sparse": True}),
                ([("created_at", -1)], {}),
                ([("discipline", 1)], {}),
                ([("authors.name", 1)], {})
            ]
            
            for fields, options in index_specs:
                try:
                    await self.db.studies.create_index(fields, **options)
                except OperationFailure as e:
                    if "equivalent index already exists" not in str(e):
                        raise
            
            logger.info("Metadata indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create metadata indexes: {e}")
            raise

    async def vector_similarity_search(
        self,
        query_vector: List[float],
        limit: int = 5,
        metadata_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search with metadata filtering"""
        try:
            pipeline = []
            
            if self.vector_search_enabled:
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
            
            if metadata_filters:
                pipeline.append({"$match": metadata_filters})
            
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

# Single instance for the application
database = DatabaseManager()
logger.info("Created global database manager instance")
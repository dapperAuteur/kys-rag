from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, List
import logging
from config import get_settings
import numpy as np

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections with fallback support"""
    
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
        
        # Try to create vector search index, fall back to regular index if not supported
        await self.setup_indexes()

    async def setup_indexes(self) -> None:
        """Create necessary database indexes with fallback options"""
        try:
            # First try to create vector search index
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
                # Create regular index on vector field
                await self.db.studies.create_index("vector")
                self.vector_search_enabled = False
            
            # Create text index for traditional text search
            await self.db.studies.create_index(
                [("title", "text"), ("text", "text"), ("topic", "text")],
                name="text_index"
            )
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise

    async def vector_similarity_search(self, query_vector: List[float], limit: int = 5) -> List[dict]:
        """
        Perform vector similarity search using appropriate method based on availability
        """
        if self.vector_search_enabled:
            # Use native vector search if available
            pipeline = [
                {
                    "$search": {
                        "index": "vector_index",
                        "knnBeta": {
                            "vector": query_vector,
                            "path": "vector",
                            "k": limit
                        }
                    }
                },
                {
                    "$project": {
                        "vector": 0,
                        "score": {"$meta": "searchScore"}
                    }
                }
            ]
            
            results = await self.db.studies.aggregate(pipeline).to_list(length=limit)
            return results
        else:
            # Fallback: Manual similarity calculation
            # Get all documents (with reasonable limit)
            all_docs = await self.db.studies.find(
                {},
                {'vector': 1, 'title': 1, 'text': 1, 'topic': 1, 'discipline': 1, 'created_at': 1}
            ).limit(1000).to_list(length=1000)
            
            # Calculate similarities
            query_vector_np = np.array(query_vector)
            similarities = []
            
            for doc in all_docs:
                if 'vector' in doc:
                    doc_vector = np.array(doc['vector'])
                    # Calculate cosine similarity
                    similarity = np.dot(query_vector_np, doc_vector) / (
                        np.linalg.norm(query_vector_np) * np.linalg.norm(doc_vector)
                    )
                    similarities.append((doc, similarity))
            
            # Sort by similarity and get top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_results = similarities[:limit]
            
            # Format results
            results = []
            for doc, score in top_results:
                doc['score'] = float(score)
                doc.pop('vector', None)  # Remove vector from result
                results.append(doc)
            
            return results

    async def close(self) -> None:
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

database = DatabaseManager()
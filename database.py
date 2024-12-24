from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging
from config import get_settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections with fallback support"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.settings = get_settings()
    
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
        
        # Ensure indexes exist
        await self.create_indexes()

    async def create_indexes(self) -> None:
        """Create necessary database indexes"""
        try:
            # Create vector search index if it doesn't exist
            indexes = await self.db.studies.list_indexes().to_list(length=None)
            index_names = [index["name"] for index in indexes]
            
            if "vector_index" not in index_names:
                logger.info("Creating vector search index...")
                await self.db.studies.create_index(
                    [("vector", "vector")],
                    name="vector_index",
                    vectorSearchOptions={
                        "numDimensions": self.settings.VECTOR_DIMENSIONS,
                        "similarity": "cosine"
                    }
                )
            
            # Create text index for traditional text search
            if "text_index" not in index_names:
                logger.info("Creating text search index...")
                await self.db.studies.create_index(
                    [("title", "text"), ("text", "text"), ("topic", "text")],
                    name="text_index"
                )
                
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise

    async def close(self) -> None:
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

database = DatabaseManager()
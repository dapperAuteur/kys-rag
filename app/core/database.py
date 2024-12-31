from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from typing import Optional, Any, Dict
import logging
from app.config import get_settings
from enum import Enum

logger = logging.getLogger(__name__)

class Collection(str, Enum):
    """Enum for collection names"""
    SCIENTIFIC_STUDIES = "scientific_studies"
    ARTICLES = "articles"
    CHAT_HISTORY = "chat_history"

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        """Initialize database manager."""
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._collections: Dict[str, AsyncIOMotorCollection] = {}
        self.settings = get_settings()
        logger.info("DatabaseManager initialized with settings")
    
    async def connect(self) -> None:
        """Connect to MongoDB Atlas."""
        if self._client is None:
            try:
                logger.info("Connecting to MongoDB Atlas...")
                self._client = AsyncIOMotorClient(
                    self.settings.MONGODB_ATLAS_URI,
                    serverSelectionTimeoutMS=5000
                )
                # Test the connection
                await self._client.admin.command('ping')
                self._db = self._client[self.settings.ACTIVE_DATABASE_NAME]
                
                # Initialize collections
                for collection in Collection:
                    self._collections[collection] = self._db[collection]
                
                logger.info(f"Successfully connected to MongoDB Atlas database: {self.settings.ACTIVE_DATABASE_NAME}")
            except Exception as e:
                self._client = None
                self._db = None
                self._collections = {}
                logger.error(f"Failed to connect to MongoDB Atlas: {e}")
                raise ConnectionError(f"Could not connect to MongoDB: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._client is not None and self._db is not None
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance, connecting if necessary."""
        if not self.is_connected:
            await self.connect()
        return self._db
    
    async def get_collection(self, collection: Collection) -> AsyncIOMotorCollection:
        """Get a specific collection, connecting if necessary."""
        if not self.is_connected:
            await self.connect()
        return self._collections[collection]
    
    async def disconnect(self) -> None:
        """Disconnect from database."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None
            self._collections = {}
            logger.info("Disconnected from database")
    
    async def health_check(self) -> bool:
        """Perform a health check on the database connection."""
        try:
            if not self.is_connected:
                await self.connect()
            await self._client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def get_scientific_studies_collection(self) -> AsyncIOMotorCollection:
        """Convenience method to get scientific studies collection."""
        return await self.get_collection(Collection.SCIENTIFIC_STUDIES)

    async def get_articles_collection(self) -> AsyncIOMotorCollection:
        """Convenience method to get articles collection."""
        return await self.get_collection(Collection.ARTICLES)

    async def get_chat_history_collection(self) -> AsyncIOMotorCollection:
        """Convenience method to get chat history collection."""
        return await self.get_collection(Collection.CHAT_HISTORY)

# Create a singleton instance
database = DatabaseManager()
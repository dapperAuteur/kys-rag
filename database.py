from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging
from config import get_settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self):
        """Initialize database manager."""
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None
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
                self._db = self._client[self.settings.DATABASE_NAME]
                logger.info(f"Successfully connected to MongoDB Atlas database: {self.settings.DATABASE_NAME}")
            except Exception as e:
                self._client = None
                self._db = None
                logger.error(f"Failed to connect to MongoDB Atlas: {e}")
                raise ConnectionError(f"Could not connect to MongoDB: {e}")
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._client is not None and self._db is not None
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database instance, connecting if necessary."""
        if not self.is_connected():
            await self.connect()
        return self._db

    async def get_client(self) -> AsyncIOMotorClient:
        """Get client instance, connecting if necessary."""
        if not self.is_connected():
            await self.connect()
        return self._client

    async def disconnect(self) -> None:
        """Disconnect from database."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("Disconnected from database")

# Create a singleton instance
database = DatabaseManager()
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional, Dict, Any
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
        try:
            logger.info("Connecting to MongoDB Atlas...")
            self._client = AsyncIOMotorClient(self.settings.MONGODB_ATLAS_URI)
            # Test the connection
            await self._client.admin.command('ping')
            # Use the database name from settings instead of the full URI
            self._db = self._client[self.settings.DATABASE_NAME]
            logger.info("Successfully connected to MongoDB Atlas")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {e}")
            raise ConnectionError(f"Could not connect to MongoDB: {e}")
    
    @property
    def client(self) -> AsyncIOMotorClient:
        """Get database client."""
        if not self._client:
            raise ConnectionError("Database not connected. Call connect() first.")
        return self._client
    
    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if not self._db:
            raise ConnectionError("Database not connected. Call connect() first.")
        return self._db
    
    async def close(self) -> None:
        """Close database connection."""
        if self._client:
            self._client.close()
            logger.info("Closed database connection")

    # Alias disconnect to close for consistent naming
    async def disconnect(self) -> None:
        """Alias for close() method."""
        await self.close()

# Create a singleton instance
database = DatabaseManager()
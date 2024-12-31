from typing import List, Dict, Any
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Handles database migration for Science Decoder refactoring"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.backup_suffix = f"_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    async def create_collections(self) -> None:
        """Create new collections if they don't exist"""
        collections = await self.db.list_collection_names()
        
        required_collections = [
            "scientific_studies",
            "articles",
            "chat_history"
        ]
        
        for collection in required_collections:
            if collection not in collections:
                await self.db.create_collection(collection)
                logger.info(f"Created collection: {collection}")

    async def create_indexes(self) -> None:
        """Create indexes for all collections"""
        # Indexes for scientific_studies collection
        await self.db.scientific_studies.create_indexes([
            {
                "name": "vector_index",
                "keys": [("vector", "2d")]
            },
            {
                "name": "topic_discipline_index",
                "keys": [("topic", 1), ("discipline", 1)]
            },
            {
                "name": "doi_index",
                "keys": [("doi", 1)],
                "unique": True,
                "sparse": True
            },
            {
                "name": "publication_date_index",
                "keys": [("publication_date", -1)]
            }
        ])
        logger.info("Created indexes for scientific_studies collection")
        
        # Indexes for articles collection
        await self.db.articles.create_indexes([
            {
                "name": "vector_index",
                "keys": [("vector", "2d")]
            },
            {
                "name": "topic_index",
                "keys": [("topic", 1)]
            },
            {
                "name": "source_url_index",
                "keys": [("source_url", 1)],
                "unique": True
            },
            {
                "name": "related_scientific_studies_index",
                "keys": [("related_scientific_studies", 1)]
            },
            {
                "name": "publication_date_index",
                "keys": [("publication_date", -1)]
            }
        ])
        logger.info("Created indexes for articles collection")
        
        # Indexes for chat_history collection
        await self.db.chat_history.create_indexes([
            {
                "name": "content_index",
                "keys": [
                    ("content_id", 1),
                    ("content_type", 1)
                ]
            },
            {
                "name": "timestamp_index",
                "keys": [("timestamp", -1)]
            }
        ])
        logger.info("Created indexes for chat_history collection")

    async def backup_existing_collection(self) -> None:
        """Create backup of existing studies collection"""
        if "studies" in await self.db.list_collection_names():
            backup_name = f"studies{self.backup_suffix}"
            await self.db.studies.aggregate([
                {"$match": {}},
                {"$out": backup_name}
            ]).to_list(None)
            logger.info(f"Created backup of studies collection: {backup_name}")

    async def migrate_existing_data(self) -> None:
        """Migrate existing studies to scientific_studies collection"""
        if "studies" in await self.db.list_collection_names():
            cursor = self.db.studies.find({})
            
            async for old_study in cursor:
                # Convert to new format
                new_study = {
                    "_id": old_study.get("_id", ObjectId()),
                    "title": old_study.get("title"),
                    "text": old_study.get("text"),
                    "topic": old_study.get("topic"),
                    "discipline": old_study.get("discipline"),
                    "vector": old_study.get("vector"),
                    "authors": [],  # Default empty list
                    "publication_date": datetime.utcnow(),
                    "journal": "Unknown",
                    "doi": None,
                    "citations": [],
                    "abstract": None,
                    "peer_reviewed": True,
                    "metadata": {},
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                # Insert into new collection
                await self.db.scientific_studies.insert_one(new_study)
            
            logger.info("Migrated existing studies to scientific_studies collection")

    async def cleanup(self) -> None:
        """Clean up old collection after successful migration"""
        if "studies" in await self.db.list_collection_names():
            await self.db.studies.drop()
            logger.info("Dropped old studies collection")

    async def run(self) -> None:
        """Run the complete migration process"""
        try:
            logger.info("Starting database migration...")
            
            # Backup existing data
            await self.backup_existing_collection()
            
            # Create new structure
            await self.create_collections()
            await self.create_indexes()
            
            # Migrate data
            await self.migrate_existing_data()
            
            # Cleanup
            await self.cleanup()
            
            logger.info("Database migration completed successfully")
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise

async def run_migration(db: AsyncIOMotorDatabase) -> None:
    """Helper function to run migration"""
    migrator = DatabaseMigration(db)
    await migrator.run()

if __name__ == "__main__":
    # This can be run as a standalone script
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.config import get_settings
    
    async def main():
        settings = get_settings()
        client = AsyncIOMotorClient(settings.MONGODB_ATLAS_URI)
        db = client[settings.ACTIVE_DATABASE_NAME]
        await run_migration(db)
    
    asyncio.run(main())
from typing import List, Dict, Any
import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
from bson import ObjectId
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT, GEO2D

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseMigration:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.backup_suffix = f"_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Initializing migration with backup suffix: {self.backup_suffix}")

    async def verify_connection(self) -> bool:
        """Verify database connection before migration"""
        try:
            await self.db.command("ping")
            logger.info("Database connection verified successfully")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    async def create_collections(self) -> None:
        """Create new collections if they don't exist"""
        try:
            collections = await self.db.list_collection_names()
            logger.info(f"Existing collections: {collections}")
            
            required_collections = [
                "scientific_studies",
                "articles",
                "chat_history"
            ]
            
            for collection in required_collections:
                if collection not in collections:
                    await self.db.create_collection(collection)
                    logger.info(f"Created collection: {collection}")
                else:
                    logger.info(f"Collection already exists: {collection}")
        except Exception as e:
            logger.error(f"Error creating collections: {e}")
            raise

    async def create_indexes(self) -> None:
        """Create indexes for all collections using proper IndexModel instances"""
        try:
            # Scientific Studies Indexes
            scientific_studies_indexes = [
                IndexModel([("vector", GEO2D)], name="vector_index"),
                IndexModel([("topic", ASCENDING), ("discipline", ASCENDING)], 
                         name="topic_discipline_index"),
                IndexModel([("doi", ASCENDING)], unique=True, sparse=True, 
                         name="doi_index"),
                IndexModel([("publication_date", DESCENDING)], 
                         name="publication_date_index")
            ]
            
            logger.info("Creating indexes for scientific_studies collection...")
            await self.db.scientific_studies.create_indexes(scientific_studies_indexes)
            
            # Articles Indexes
            articles_indexes = [
                IndexModel([("vector", GEO2D)], name="vector_index"),
                IndexModel([("topic", ASCENDING)], name="topic_index"),
                IndexModel([("source_url", ASCENDING)], unique=True, 
                         name="source_url_index"),
                IndexModel([("related_scientific_studies", ASCENDING)], 
                         name="related_scientific_studies_index"),
                IndexModel([("publication_date", DESCENDING)], 
                         name="publication_date_index")
            ]
            
            logger.info("Creating indexes for articles collection...")
            await self.db.articles.create_indexes(articles_indexes)
            
            # Chat History Indexes
            chat_history_indexes = [
                IndexModel(
                    [("content_id", ASCENDING), ("content_type", ASCENDING)],
                    name="content_index"
                ),
                IndexModel([("timestamp", DESCENDING)], name="timestamp_index")
            ]
            
            logger.info("Creating indexes for chat_history collection...")
            await self.db.chat_history.create_indexes(chat_history_indexes)
            
            logger.info("Successfully created all indexes")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            raise

    async def backup_existing_collection(self) -> None:
        """Create backup of existing studies collection"""
        try:
            collections = await self.db.list_collection_names()
            if "studies" in collections:
                backup_name = f"studies{self.backup_suffix}"
                await self.db.studies.aggregate([
                    {"$match": {}},
                    {"$out": backup_name}
                ]).to_list(None)
                logger.info(f"Created backup of studies collection: {backup_name}")
            else:
                logger.info("No existing studies collection to backup")
        except Exception as e:
            logger.error(f"Error during backup: {e}")
            raise

    async def migrate_existing_data(self) -> None:
        """Migrate existing studies to scientific_studies collection"""
        try:
            if "studies" in await self.db.list_collection_names():
                cursor = self.db.studies.find({})
                migration_count = 0
                
                async for old_study in cursor:
                    new_study = {
                        "_id": old_study.get("_id", ObjectId()),
                        "title": old_study.get("title"),
                        "text": old_study.get("text"),
                        "topic": old_study.get("topic"),
                        "discipline": old_study.get("discipline"),
                        "vector": old_study.get("vector"),
                        "authors": [],
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
                    
                    await self.db.scientific_studies.insert_one(new_study)
                    migration_count += 1
                
                logger.info(f"Migrated {migration_count} studies to scientific_studies collection")
            else:
                logger.info("No existing studies to migrate")
        except Exception as e:
            logger.error(f"Error during migration: {e}")
            raise

    async def cleanup(self) -> None:
        """Clean up old collection after successful migration"""
        try:
            if "studies" in await self.db.list_collection_names():
                await self.db.studies.drop()
                logger.info("Dropped old studies collection")
            else:
                logger.info("No old studies collection to clean up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise

    async def run(self) -> None:
        """Run the complete migration process"""
        try:
            logger.info("Starting database migration...")
            
            if not await self.verify_connection():
                raise ConnectionError("Could not verify database connection")
            
            await self.backup_existing_collection()
            await self.create_collections()
            await self.create_indexes()
            await self.migrate_existing_data()
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
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.core.config import get_settings
    
    async def main():
        settings = get_settings()
        client = AsyncIOMotorClient(settings.MONGODB_ATLAS_URI)
        db = client[settings.ACTIVE_DATABASE_NAME]
        await run_migration(db)
    
    asyncio.run(main())
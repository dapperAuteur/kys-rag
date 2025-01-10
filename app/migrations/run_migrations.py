# app/migrations/run_migrations.py

import asyncio
import logging
import argparse
from typing import List, Type
from datetime import datetime
from multiprocessing import freeze_support
from .base import BaseMigration
from .vector_migrations import UpdateArticleVectors, UpdateStudyVectors
from app.core.database import database

logger = logging.getLogger(__name__)

# List of available migrations
MIGRATIONS: List[Type[BaseMigration]] = [
    UpdateArticleVectors,
    UpdateStudyVectors
]

async def setup_migrations_collection():
    """Ensure migrations collection exists with proper indexes."""
    try:
        migrations_coll = await database.get_collection('migrations')
        
        # Create indexes
        await migrations_coll.create_index('name', unique=True)
        await migrations_coll.create_index('status')
        await migrations_coll.create_index('timestamp')
        
    except Exception as e:
        logger.error(f"Error setting up migrations collection: {e}")
        raise

async def get_migration_status(migration_name: str) -> str:
    """Get the status of a specific migration."""
    migrations_coll = await database.get_collection('migrations')
    result = await migrations_coll.find_one({'name': migration_name})
    return result['status'] if result else 'pending'

async def run_migrations(specific_migration: str = None, force: bool = False):
    """Run database migrations."""
    try:
        await database.connect()
        await setup_migrations_collection()
        
        for migration_class in MIGRATIONS:
            migration_name = migration_class.__name__
            
            # Skip if not the specified migration
            if specific_migration and migration_name != specific_migration:
                continue
            
            # Check if migration has already been run
            status = await get_migration_status(migration_name)
            if status == 'completed' and not force:
                logger.info(f"Skipping completed migration: {migration_name}")
                continue
            
            # Run migration
            logger.info(f"Running migration: {migration_name}")
            migration = migration_class()
            await migration.run()
            
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise
    
    finally:
        await database.disconnect()

def main():
    """Main entry point for migration runner."""
    parser = argparse.ArgumentParser(description='Run database migrations')
    parser.add_argument(
        '--migration',
        help='Specific migration to run'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force run even if migration was previously completed'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Batch size for processing documents'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run migrations
    asyncio.run(run_migrations(args.migration, args.force))

if __name__ == '__main__':
    freeze_support()  # Added for multiprocessing support
    main()
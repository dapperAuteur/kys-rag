import pytest
import logging
from typing import AsyncGenerator
from database import database

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable asyncio for pytest
pytest_plugins = [
    "pytest_asyncio"
]

@pytest.fixture(autouse=True)
async def setup_test_database() -> AsyncGenerator:
    """Setup test database connection and cleanup after tests"""
    logger.info("Setting up test database connection...")
    
    # Connect to database
    await database.connect()
    
    # Clear test collections before each test
    await database.db.studies.delete_many({})
    await database.db.articles.delete_many({})
    
    yield
    
    # Cleanup after tests
    logger.info("Cleaning up test database...")
    await database.db.studies.delete_many({})
    await database.db.articles.delete_many({})
    await database.close()
import pytest
from database import DatabaseManager, database
import logging
from datetime import datetime
from bson import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
async def setup_teardown():
    """Setup and teardown test database"""
    logger.info("Setting up test database...")
    
    # Connect to database
    await database.connect()
    
    # Clear test collections
    await database.db.studies.delete_many({})
    await database.db.articles.delete_many({})
    
    yield
    
    # Cleanup
    logger.info("Cleaning up test database...")
    await database.db.studies.delete_many({})
    await database.db.articles.delete_many({})
    await database.close()

async def test_database_connection():
    """Test database connection"""
    logger.info("Testing database connection...")
    
    # Create new connection
    db = DatabaseManager()
    await db.connect()
    
    # Verify connection
    assert db._client is not None
    assert db._db is not None
    
    # Verify indexes
    indexes = await db.db.studies.list_indexes().to_list(None)
    assert any('vector' in idx['name'] for idx in indexes)
    assert any('text' in idx['name'] for idx in indexes)
    
    logger.info("Database connection test passed")

async def test_study_operations():
    """Test study collection operations"""
    logger.info("Testing study operations...")
    
    # Test data
    study = {
        "title": "Test Study",
        "text": "This is a test study",
        "authors": ["Test Author"],
        "publication_date": datetime.utcnow(),
        "vector": [0.1] * 768  # Test vector
    }
    
    # Insert study
    result = await database.db.studies.insert_one(study)
    assert result.inserted_id is not None
    
    # Retrieve study
    saved_study = await database.db.studies.find_one(
        {"_id": result.inserted_id}
    )
    assert saved_study["title"] == study["title"]
    
    logger.info("Study operations test passed")

async def test_article_operations():
    """Test article collection operations"""
    logger.info("Testing article operations...")
    
    # Create test study first
    study = {
        "title": "Referenced Study",
        "text": "This is a referenced study",
        "authors": ["Study Author"],
        "vector": [0.1] * 768
    }
    study_result = await database.db.studies.insert_one(study)
    
    # Test article data
    article = {
        "title": "Test Article",
        "text": "This is a test article",
        "url": "https://example.com/test",
        "cited_studies": [str(study_result.inserted_id)],
        "vector": [0.2] * 768
    }
    
    # Insert article
    result = await database.db.articles.insert_one(article)
    assert result.inserted_id is not None
    
    # Retrieve article
    saved_article = await database.db.articles.find_one(
        {"_id": result.inserted_id}
    )
    assert saved_article["title"] == article["title"]
    assert len(saved_article["cited_studies"]) == 1
    
    logger.info("Article operations test passed")

async def test_vector_search():
    """Test vector similarity search"""
    logger.info("Testing vector search...")
    
    if not database.vector_search_enabled:
        logger.warning("Vector search not available, skipping test")
        return
        
    # Insert test study with vector
    study = {
        "title": "Vector Test Study",
        "text": "This is a test for vector search",
        "authors": ["Vector Author"],
        "vector": [0.
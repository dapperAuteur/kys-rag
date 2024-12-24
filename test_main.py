import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import json
import logging
from main import app
from database import database
from models import Study, SearchQuery, Source, SourceType, Author
from bson import ObjectId

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def test_client():
    """Create a test client instance"""
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
async def setup_teardown():
    """Setup and teardown the test database"""
    logger.info("Setting up test database...")
    await database.connect()
    await database.db.studies.delete_many({})

    yield

    logger.info("Cleaning up test database...")
    await database.db.studies.delete_many({})
    await database.close()

def test_root(test_client):
    """Test the root endpoint"""
    logger.info("Testing root endpoint...")
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    logger.info("Root endpoint test successful")

def test_create_study_from_pdf(test_client):
    """Test creating a study from a PDF source"""
    logger.info("Testing study creation from PDF...")
    
    # Create test study data
    study_data = {
        "title": "Test Study",
        "text": "This is a test study about science.",
        "topic": "Testing",
        "discipline": "Computer Science",
        "authors": [{"name": "Test Author"}],
        "source": {
            "type": "scientific_study",
            "pdf_path": "tests/data/test_study.pdf",
            "title": "Test PDF Study",
            "authors": [{"name": "PDF Author"}]
        }
    }
    
    response = test_client.post("/studies/", json=study_data)
    assert response.status_code == 200
    data = response.json()
    assert "details" in data
    study_id = data["details"]["id"]
    logger.info(f"Study created with ID: {study_id}")
    
    # Verify study was saved
    response = test_client.get(f"/studies/{study_id}")
    assert response.status_code == 200
    saved_study = response.json()
    assert saved_study["title"] == study_data["title"]
    assert "text_chunks" in saved_study["source"]
    logger.info("Study creation from PDF successful")

def test_create_study_from_url(test_client):
    """Test creating a study from a URL source"""
    logger.info("Testing study creation from URL...")
    
    study_data = {
        "title": "Test Article",
        "text": "This is a test article about science.",
        "topic": "Testing",
        "discipline": "Science Communication",
        "authors": [{"name": "Test Author"}],
        "source": {
            "type": "article",
            "url": "https://example.com/article",
            "title": "Test Web Article",
            "authors": [{"name": "Web Author"}]
        }
    }
    
    response = test_client.post("/studies/", json=study_data)
    assert response.status_code == 200
    data = response.json()
    study_id = data["details"]["id"]
    logger.info(f"Article created with ID: {study_id}")
    
    # Verify article was saved
    response = test_client.get(f"/studies/{study_id}")
    assert response.status_code == 200
    saved_study = response.json()
    assert saved_study["title"] == study_data["title"]
    assert "text_chunks" in saved_study["source"]
    logger.info("Study creation from URL successful")

def test_search_with_filters(test_client):
    """Test search functionality with metadata filters"""
    logger.info("Testing search with metadata filters...")
    
    # First create some test studies
    study_data = [
        {
            "title": "AI Study",
            "text": "This study focuses on artificial intelligence.",
            "topic": "AI",
            "discipline": "Computer Science",
            "authors": [{"name": "AI Author"}],
            "source": {
                "type": "scientific_study",
                "pdf_path": "tests/data/ai_study.pdf",
                "title": "AI Research",
                "authors": [{"name": "AI Researcher"}]
            }
        },
        {
            "title": "AI Article",
            "text": "This article discusses AI research.",
            "topic": "AI",
            "discipline": "Science Communication",
            "authors": [{"name": "Science Writer"}],
            "source": {
                "type": "article",
                "url": "https://example.com/ai-article",
                "title": "AI News",
                "authors": [{"name": "Web Author"}]
            }
        }
    ]
    
    study_ids = []
    for data in study_data:
        response = test_client.post("/studies/", json=data)
        assert response.status_code == 200
        study_ids.append(response.json()["details"]["id"])
    
    logger.info("Created test studies for search")
    
    # Test search with filters
    search_query = {
        "query_text": "artificial intelligence",
        "limit": 5,
        "min_score": 0.0,
        "source_type": "scientific_study",
        "discipline": "Computer Science"
    }
    
    response = test_client.post("/search/", json=search_query)
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    
    # Verify only scientific studies are returned
    for result in results:
        assert result["study"]["source"]["type"] == "scientific_study"
        assert result["study"]["discipline"] == "Computer Science"
    
    logger.info("Search with filters successful")

def test_invalid_study_id(test_client):
    """Test retrieval with invalid study ID"""
    logger.info("Testing invalid study ID handling...")
    response = test_client.get(f"/studies/{str(ObjectId())}")
    assert response.status_code == 404
    logger.info("Invalid study ID test successful")
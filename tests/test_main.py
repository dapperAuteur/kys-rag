import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import json
import logging
from main import app
from database import database
from models import Study, Article, SearchQuery
from bson import ObjectId

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application"""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_study():
    """Create a sample study for testing"""
    return {
        "title": "Test Study on Brain Function",
        "text": "This is a scientific study about brain function and cognition.",
        "authors": [
            {
                "name": "Dr. Jane Smith",
                "email": "jane.smith@university.edu",
                "institution": "Research University"
            }
        ],
        "discipline": "Neuroscience",
        "keywords": ["brain", "cognition", "research"],
        "publication_date": datetime.utcnow().isoformat()
    }

@pytest.fixture
def sample_article():
    """Create a sample article for testing"""
    return {
        "title": "New Discoveries in Brain Research",
        "text": "Scientists have made remarkable discoveries about brain function.",
        "url": "https://example.com/brain-research",
        "authors": [
            {
                "name": "John Writer",
                "email": "john.writer@news.com"
            }
        ],
        "cited_studies": []  # Will be filled with actual study ID in tests
    }

def test_read_root(test_client):
    """Test the root endpoint"""
    logger.info("Testing root endpoint...")
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    logger.info("Root endpoint test passed")

async def test_create_study(test_client, sample_study):
    """Test creating a new scientific study"""
    logger.info("Testing study creation...")
    
    response = test_client.post(
        "/studies/",
        json=sample_study
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data["details"]
    study_id = data["details"]["id"]
    
    # Verify study was saved correctly
    response = test_client.get(f"/studies/{study_id}")
    assert response.status_code == 200
    saved_study = response.json()
    assert saved_study["title"] == sample_study["title"]
    assert len(saved_study["text_chunks"]) > 0
    
    logger.info("Study creation test passed")

async def test_create_article_with_citation(test_client, sample_study, sample_article):
    """Test creating an article that cites a study"""
    logger.info("Testing article creation with citation...")
    
    # First create a study to cite
    study_response = test_client.post(
        "/studies/",
        json=sample_study
    )
    study_id = study_response.json()["details"]["id"]
    
    # Add study ID to article citations
    sample_article["cited_studies"] = [study_id]
    
    # Create article
    response = test_client.post(
        "/articles/",
        json=sample_article
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data["details"]
    article_id = data["details"]["id"]
    
    # Verify article was saved correctly
    response = test_client.get(f"/articles/{article_id}")
    assert response.status_code == 200
    saved_article = response.json()
    assert saved_article["title"] == sample_article["title"]
    assert study_id in saved_article["cited_studies"]
    
    logger.info("Article creation test passed")

async def test_search_content(test_client, sample_study, sample_article):
    """Test searching across studies and articles"""
    logger.info("Testing content search...")
    
    # Create test data
    study_response = test_client.post("/studies/", json=sample_study)
    study_id = study_response.json()["details"]["id"]
    
    sample_article["cited_studies"] = [study_id]
    test_client.post("/articles/", json=sample_article)
    
    # Test search
    search_query = {
        "query_text": "brain function research",
        "content_type": "all",
        "limit": 5,
        "min_score": 0.0
    }
    
    response = test_client.post("/search/", json=search_query)
    assert response.status_code == 200
    results = response.json()
    
    # Verify we get both types of content
    content_types = {result["content_type"] for result in results}
    assert "study" in content_types
    assert "article" in content_types
    
    logger.info("Search test passed")

async def test_invalid_study_id(test_client):
    """Test handling of invalid study ID"""
    logger.info("Testing invalid study ID handling...")
    response = test_client.get(f"/studies/{str(ObjectId())}")
    assert response.status_code == 404
    logger.info("Invalid study ID test passed")

async def test_invalid_article_citation(test_client, sample_article):
    """Test article creation with invalid study citation"""
    logger.info("Testing invalid citation handling...")
    
    # Try to create article citing non-existent study
    sample_article["cited_studies"] = [str(ObjectId())]
    response = test_client.post("/articles/", json=sample_article)
    assert response.status_code == 404
    assert "Cited study not found" in response.json()["detail"]
    
    logger.info("Invalid citation test passed")
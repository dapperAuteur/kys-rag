import pytest
from fastapi.testclient import TestClient
from main import app  # Import the app instance from main.py
from database import database
from models import Study, SearchQuery
from bson import ObjectId

@pytest.fixture(scope="module")
def test_client():
    """Fixture to return a TestClient"""
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test"""
    # Setup
    database.connect()
    database.db.studies.delete_many({})

    yield

    # Teardown
    database.db.studies.delete_many({})
    database.close()

def test_root(test_client):
    """Test root endpoint"""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

def test_create_and_retrieve_study(test_client):
    """Test study creation and retrieval"""
    # Create study
    study_data = {
        "title": "Test Study",
        "text": "This is a test study about science.",
        "topic": "Testing",
        "discipline": "Computer Science"
    }
    
    response = test_client.post("/studies/", json=study_data)
    assert response.status_code == 200
    data = response.json()
    assert "details" in data
    study_id = data["details"]["id"]
    
    # Retrieve study
    response = test_client.get(f"/studies/{study_id}")
    assert response.status_code == 200
    study = response.json()
    assert study["title"] == study_data["title"]

def test_search_studies(test_client):
    """Test vector similarity search"""
    # Create test studies
    study_data = [
        {
            "title": "AI Study",
            "text": "This study focuses on artificial intelligence.",
            "topic": "AI",
            "discipline": "Computer Science"
        },
        {
            "title": "Biology Study",
            "text": "This study examines cell biology.",
            "topic": "Biology",
            "discipline": "Life Sciences"
        }
    ]
    
    for data in study_data:
        response = test_client.post("/studies/", json=data)
        assert response.status_code == 200
    
    # Search for AI-related studies
    search_query = {
        "query_text": "artificial intelligence research",
        "limit": 5,
        "min_score": 0.0
    }
    
    response = test_client.post("/search/", json=search_query)
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0

def test_invalid_study_id(test_client):
    """Test retrieval with invalid study ID"""
    response = test_client.get(f"/studies/{str(ObjectId())}")
    assert response.status_code == 404

import pytest
from httpx import AsyncClient
from typing import AsyncGenerator
import pytest_asyncio
from main import app
from database import database
from models import Study, SearchQuery
from bson import ObjectId

@pytest_asyncio.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(autouse=True)
async def setup_teardown():
    """Setup and teardown for each test"""
    # Setup
    await database.connect()
    # Clear test database
    await database.db.studies.delete_many({})
    
    yield
    
    # Teardown
    await database.db.studies.delete_many({})
    await database.close()

async def test_root(test_client):
    """Test root endpoint"""
    response = await test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

async def test_create_and_retrieve_study(test_client):
    """Test study creation and retrieval"""
    # Create study
    study_data = {
        "title": "Test Study",
        "text": "This is a test study about science.",
        "topic": "Testing",
        "discipline": "Computer Science"
    }
    
    response = await test_client.post("/studies/", json=study_data)
    assert response.status_code == 200
    data = response.json()
    assert "details" in data
    study_id = data["details"]["id"]
    
    # Retrieve study
    response = await test_client.get(f"/studies/{study_id}")
    assert response.status_code == 200
    study = response.json()
    assert study["title"] == study_data["title"]

async def test_search_studies(test_client):
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
        response = await test_client.post("/studies/", json=data)
        assert response.status_code == 200
    
    # Search for AI-related studies
    search_query = {
        "query_text": "artificial intelligence research",
        "limit": 5,
        "min_score": 0.0
    }
    
    response = await test_client.post("/search/", json=search_query)
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0

async def test_invalid_study_id(test_client):
    """Test retrieval with invalid study ID"""
    response = await test_client.get(f"/studies/{str(ObjectId())}")
    assert response.status_code == 404
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from bson import ObjectId

pytestmark = pytest.mark.asyncio

def test_root(client: TestClient):
    """Test root endpoint using sync client"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "Welcome to the Science Decoder API!"

async def test_create_and_retrieve_study(async_client: AsyncClient):
    """Test study creation and retrieval using async client"""
    study_data = {
        "title": "Test Study",
        "text": "This is a test study about science.",
        "topic": "Testing",
        "discipline": "Computer Science"
    }
    
    # Create study
    response = await async_client.post("/studies/", json=study_data)
    assert response.status_code == 200, f"Failed to create study: {response.text}"
    data = response.json()
    assert "details" in data
    study_id = data["details"]["id"]
    
    # Retrieve study
    response = await async_client.get(f"/studies/{study_id}")
    assert response.status_code == 200, f"Failed to retrieve study: {response.text}"
    study = response.json()
    assert study["title"] == study_data["title"]

async def test_search_studies(async_client: AsyncClient):
    """Test vector similarity search using async client"""
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
    
    # Create test studies
    created_studies = []
    for data in study_data:
        response = await async_client.post("/studies/", json=data)
        assert response.status_code == 200, f"Failed to create study: {response.text}"
        created_studies.append(response.json()["details"]["id"])
    
    # Test search
    search_query = {
        "query_text": "artificial intelligence research",
        "limit": 5,
        "min_score": 0.0
    }
    
    response = await async_client.post("/search/", json=search_query)
    assert response.status_code == 200, f"Search failed: {response.text}"
    results = response.json()
    assert len(results) > 0, "Search returned no results"

async def test_invalid_study_id(async_client: AsyncClient):
    """Test retrieval with invalid study ID using async client"""
    non_existent_id = str(ObjectId())
    response = await async_client.get(f"/studies/{non_existent_id}")
    assert response.status_code == 404, "Should return 404 for non-existent study"
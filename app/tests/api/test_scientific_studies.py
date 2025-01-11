import pytest
from httpx import AsyncClient
from datetime import datetime
from bson import ObjectId

pytestmark = pytest.mark.asyncio

async def test_create_scientific_study(async_client: AsyncClient):
    """Test creating a scientific study."""
    study_data = {
        "title": "Test Scientific Study",
        "text": "This is a test scientific study about AI.",
        "authors": ["John Doe", "Jane Smith"],
        "publication_date": datetime.utcnow().isoformat(),
        "journal": "Test Journal",
        "topic": "Artificial Intelligence",
        "discipline": "Computer Science",
        "abstract": "A test study abstract"
    }
    
    response = await async_client.post("/scientific-studies/", json=study_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data["details"]
    
    # Verify study was created
    study_id = data["details"]["id"]
    get_response = await async_client.get(f"/scientific-studies/{study_id}")
    assert get_response.status_code == 200
    created_study = get_response.json()
    assert created_study["title"] == study_data["title"]

async def test_get_nonexistent_scientific_study(async_client: AsyncClient):
    """Test retrieving a non-existent scientific study."""
    fake_id = str(ObjectId())
    response = await async_client.get(f"/scientific-studies/{fake_id}")
    assert response.status_code == 404

async def test_update_scientific_study(async_client: AsyncClient):
    """Test updating a scientific study."""
    # First create a study
    initial_data = {
        "title": "Initial Title",
        "text": "Initial text.",
        "authors": ["John Doe"],
        "publication_date": datetime.utcnow().isoformat(),
        "journal": "Test Journal",
        "topic": "Testing",
        "discipline": "Computer Science"
    }
    
    create_response = await async_client.post("/scientific-studies/", json=initial_data)
    study_id = create_response.json()["details"]["id"]
    
    # Update the study
    updated_data = {
        **initial_data,
        "title": "Updated Title",
        "text": "Updated text."
    }
    
    update_response = await async_client.put(
        f"/scientific-studies/{study_id}",
        json=updated_data
    )
    assert update_response.status_code == 200
    
    # Verify update
    get_response = await async_client.get(f"/scientific-studies/{study_id}")
    updated_study = get_response.json()
    assert updated_study["title"] == "Updated Title"
    assert updated_study["text"] == "Updated text."

async def test_delete_scientific_study(async_client: AsyncClient):
    """Test deleting a scientific study."""
    # First create a study
    study_data = {
        "title": "Study to Delete",
        "text": "This study will be deleted.",
        "authors": ["John Doe"],
        "publication_date": datetime.utcnow().isoformat(),
        "journal": "Test Journal",
        "topic": "Testing",
        "discipline": "Computer Science"
    }
    
    create_response = await async_client.post("/scientific-studies/", json=study_data)
    study_id = create_response.json()["details"]["id"]
    
    # Delete the study
    delete_response = await async_client.delete(f"/scientific-studies/{study_id}")
    assert delete_response.status_code == 200
    
    # Verify deletion
    get_response = await async_client.get(f"/scientific-studies/{study_id}")
    assert get_response.status_code == 404

async def test_search_scientific_studies(async_client: AsyncClient):
    """Test searching scientific studies."""
    # Create some test studies
    study_data = [
        {
            "title": "AI in Healthcare",
            "text": "Study about artificial intelligence in healthcare.",
            "authors": ["John Doe"],
            "publication_date": datetime.utcnow().isoformat(),
            "journal": "AI Journal",
            "topic": "AI Healthcare",
            "discipline": "Computer Science"
        },
        {
            "title": "Climate Change Effects",
            "text": "Study about climate change impacts.",
            "authors": ["Jane Smith"],
            "publication_date": datetime.utcnow().isoformat(),
            "journal": "Climate Journal",
            "topic": "Climate",
            "discipline": "Environmental Science"
        }
    ]
    
    for study in study_data:
        await async_client.post("/scientific-studies/", json=study)
    
    # Test search
    response = await async_client.post(
        "/scientific-studies/search",
        params={"query_text": "artificial intelligence healthcare"}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert any("AI" in result["content"]["title"] for result in results)

async def test_get_scientific_studies_by_discipline(async_client: AsyncClient):
    """Test getting scientific studies by discipline."""
    # Create test studies with different disciplines
    study_data = [
        {
            "title": "CS Study 1",
            "text": "Computer Science study 1.",
            "authors": ["John Doe"],
            "publication_date": datetime.utcnow().isoformat(),
            "journal": "CS Journal",
            "topic": "AI",
            "discipline": "Computer Science"
        },
        {
            "title": "CS Study 2",
            "text": "Computer Science study 2.",
            "authors": ["Jane Smith"],
            "publication_date": datetime.utcnow().isoformat(),
            "journal": "CS Journal",
            "topic": "Databases",
            "discipline": "Computer Science"
        },
        {
            "title": "Biology Study",
            "text": "Biology research.",
            "authors": ["Alice Brown"],
            "publication_date": datetime.utcnow().isoformat(),
            "journal": "Bio Journal",
            "topic": "Genetics",
            "discipline": "Biology"
        }
    ]
    
    for study in study_data:
        await async_client.post("/scientific-studies/", json=study)
    
    # Test getting studies by discipline
    response = await async_client.get(
        "/scientific-studies/discipline/Computer Science",
        params={"limit": 10}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert all(study["discipline"] == "Computer Science" for study in results)

async def test_update_citations(async_client: AsyncClient):
    """Test updating citations for a scientific study."""
    # Create a study
    study_data = {
        "title": "Study with Citations",
        "text": "Study text with references.",
        "authors": ["John Doe"],
        "publication_date": datetime.utcnow().isoformat(),
        "journal": "Test Journal",
        "topic": "Testing",
        "discipline": "Computer Science"
    }
    
    create_response = await async_client.post("/scientific-studies/", json=study_data)
    study_id = create_response.json()["details"]["id"]
    
    # Update citations
    citations = [
        "Citation 1",
        "Citation 2",
        "Citation 3"
    ]
    
    response = await async_client.put(
        f"/scientific-studies/{study_id}/citations",
        json=citations
    )
    assert response.status_code == 200
    
    # Verify citations were updated
    get_response = await async_client.get(f"/scientific-studies/{study_id}")
    updated_study = get_response.json()
    assert "citations" in updated_study
    assert len(updated_study["citations"]) == 3
    assert updated_study["citations"] == citations
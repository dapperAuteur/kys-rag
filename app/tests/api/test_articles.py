import pytest
from httpx import AsyncClient
from datetime import datetime
from bson import ObjectId

pytestmark = pytest.mark.asyncio

async def test_create_article(async_client: AsyncClient):
    """Test creating an article."""
    article_data = {
        "title": "Test Article",
        "text": "This is a test article about AI research.",
        "author": "John Journalist",
        "publication_date": datetime.utcnow().isoformat(),
        "source_url": "https://example.com/test-article",
        "publication_name": "Tech News",
        "topic": "Artificial Intelligence",
        "article_type": "news"
    }
    
    response = await async_client.post("/articles/", json=article_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "id" in data["details"]
    
    # Verify article was created
    article_id = data["details"]["id"]
    get_response = await async_client.get(f"/articles/{article_id}")
    assert get_response.status_code == 200
    created_article = get_response.json()
    assert created_article["title"] == article_data["title"]

async def test_get_nonexistent_article(async_client: AsyncClient):
    """Test retrieving a non-existent article."""
    fake_id = str(ObjectId())
    response = await async_client.get(f"/articles/{fake_id}")
    assert response.status_code == 404

async def test_update_article(async_client: AsyncClient):
    """Test updating an article."""
    # First create an article
    initial_data = {
        "title": "Initial Article",
        "text": "Initial text.",
        "author": "John Journalist",
        "publication_date": datetime.utcnow().isoformat(),
        "source_url": "https://example.com/initial",
        "publication_name": "Tech News",
        "topic": "Technology",
        "article_type": "news"
    }
    
    create_response = await async_client.post("/articles/", json=initial_data)
    article_id = create_response.json()["details"]["id"]
    
    # Update the article
    updated_data = {
        **initial_data,
        "title": "Updated Article",
        "text": "Updated text.",
        "source_url": "https://example.com/updated"
    }
    
    update_response = await async_client.put(
        f"/articles/{article_id}",
        json=updated_data
    )
    assert update_response.status_code == 200
    
    # Verify update
    get_response = await async_client.get(f"/articles/{article_id}")
    updated_article = get_response.json()
    assert updated_article["title"] == "Updated Article"
    assert updated_article["text"] == "Updated text."

async def test_add_and_verify_claim(async_client: AsyncClient):
    """Test adding and verifying a claim in an article."""
    # Create an article
    article_data = {
        "title": "Article with Claims",
        "text": "Article text with scientific claims.",
        "author": "John Journalist",
        "publication_date": datetime.utcnow().isoformat(),
        "source_url": "https://example.com/claims",
        "publication_name": "Science News",
        "topic": "Science",
        "article_type": "news"
    }
    
    create_response = await async_client.post("/articles/", json=article_data)
    article_id = create_response.json()["details"]["id"]
    
    # Add a claim
    claim_data = {
        "text": "AI improves medical diagnosis accuracy by 50%",
        "confidence_score": None,
        "verified": False,
        "context": "Research results section"
    }
    
    add_claim_response = await async_client.post(
        f"/articles/{article_id}/claims",
        json=claim_data
    )
    assert add_claim_response.status_code == 200
    
    # Verify the claim
    verify_response = await async_client.put(
        f"/articles/{article_id}/claims/0/verify",
        params={
            "verification_notes": "Verified with recent studies",
            "confidence_score": 0.85,
            "verified": True
        }
    )
    assert verify_response.status_code == 200
    
    # Check if claim was updated
    get_response = await async_client.get(f"/articles/{article_id}")
    article = get_response.json()
    assert len(article["claims"]) == 1
    assert article["claims"][0]["verified"] == True
    assert article["claims"][0]["confidence_score"] == 0.85

async def test_link_scientific_study_to_article(async_client: AsyncClient):
    """Test linking a scientific study to an article."""
    # Create a scientific study
    study_data = {
        "title": "Original Research",
        "text": "Scientific study text.",
        "authors": ["Researcher"],
        "publication_date": datetime.utcnow().isoformat(),
        "journal": "Science Journal",
        "topic": "Research",
        "discipline": "Science"
    }
    
    study_response = await async_client.post("/scientific-studies/", json=study_data)
    study_id = study_response.json()["details"]["id"]
    
    # Create an article
    article_data = {
        "title": "Article About Research",
        "text": "Article discussing research.",
        "author": "Journalist",
        "publication_date": datetime.utcnow().isoformat(),
        "source_url": "https://example.com/research",
        "publication_name": "News",
        "topic": "Science",
        "article_type": "news"
    }
    
    article_response = await async_client.post("/articles/", json=article_data)
    article_id = article_response.json()["details"]["id"]
    
    # Link study to article
    link_response = await async_client.post(
        f"/articles/{article_id}/scientific-studies/{study_id}"
    )
    assert link_response.status_code == 200
    
    # Verify link
    get_studies_response = await async_client.get(
        f"/articles/{article_id}/scientific-studies"
    )
    assert get_studies_response.status_code == 200
    related_studies = get_studies_response.json()
    assert len(related_studies) == 1
    assert related_studies[0]["title"] == study_data["title"]

async def test_search_articles(async_client: AsyncClient):
    """Test searching articles."""
    # Create test articles
    article_data = [
        {
            "title": "AI in Medicine",
            "text": "Article about artificial intelligence in healthcare.",
            "author": "John Journalist",
            "publication_date": datetime.utcnow().isoformat(),
            "source_url": "https://example.com/ai-medicine",
            "publication_name": "Tech News",
            "topic": "AI Healthcare",
            "article_type": "news"
        },
        {
            "title": "Climate Research Update",
            "text": "Latest findings in climate change research.",
            "author": "Jane Reporter",
            "publication_date": datetime.utcnow().isoformat(),
            "source_url": "https://example.com/climate",
            "publication_name": "Science Daily",
            "topic": "Climate",
            "article_type": "news"
        }
    ]
    
    for article in article_data:
        await async_client.post("/articles/", json=article)
    
    # Test search
    response = await async_client.post(
        "/articles/search",
        params={"query_text": "artificial intelligence healthcare"}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert any("AI" in result["content"]["title"] for result in results)
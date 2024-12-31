import pytest
from httpx import AsyncClient
from datetime import datetime
import json

pytestmark = pytest.mark.asyncio

async def create_test_data(async_client: AsyncClient):
    """Helper function to create test data."""
    # Create scientific studies
    study_data = [
        {
            "title": "AI in Healthcare Research",
            "text": "Scientific study about AI applications in medicine.",
            "authors": ["Researcher One"],
            "publication_date": datetime.utcnow().isoformat(),
            "journal": "AI Medical Journal",
            "topic": "AI Healthcare",
            "discipline": "Computer Science"
        },
        {
            "title": "Climate Impact Study",
            "text": "Research on climate change effects.",
            "authors": ["Researcher Two"],
            "publication_date": datetime.utcnow().isoformat(),
            "journal": "Climate Science",
            "topic": "Climate",
            "discipline": "Environmental Science"
        }
    ]
    
    # Create articles
    article_data = [
        {
            "title": "New AI Medical Breakthrough",
            "text": "Article about recent AI healthcare developments.",
            "author": "John Journalist",
            "publication_date": datetime.utcnow().isoformat(),
            "source_url": "https://example.com/ai-medical",
            "publication_name": "Tech News",
            "topic": "AI Healthcare",
            "article_type": "news"
        },
        {
            "title": "Understanding Climate Change",
            "text": "Overview of recent climate research.",
            "author": "Jane Reporter",
            "publication_date": datetime.utcnow().isoformat(),
            "source_url": "https://example.com/climate-overview",
            "publication_name": "Science Daily",
            "topic": "Climate",
            "article_type": "news"
        }
    ]
    
    # Insert test data
    for study in study_data:
        await async_client.post("/scientific-studies/", json=study)
    
    for article in article_data:
        await async_client.post("/articles/", json=article)

async def test_search_all_content(async_client: AsyncClient):
    """Test searching across all content types."""
    await create_test_data(async_client)
    
    search_query = {
        "query_text": "AI healthcare medicine",
        "limit": 10,
        "min_score": 0.1
    }
    
    response = await async_client.post("/search/", json=search_query)
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    # Check if results contain both studies and articles
    content_types = {result["content_type"] for result in results}
    assert "scientific_study" in content_types or "article" in content_types

async def test_search_by_content_type(async_client: AsyncClient):
    """Test searching with content type filter."""
    await create_test_data(async_client)
    
    # Search only scientific studies
    study_query = {
        "query_text": "AI healthcare",
        "content_type": "scientific_study",
        "limit": 10,
        "min_score": 0.1
    }
    
    study_response = await async_client.post("/search/", json=study_query)
    assert study_response.status_code == 200
    study_results = study_response.json()
    assert all(r["content_type"] == "scientific_study" for r in study_results)
    
    # Search only articles
    article_query = {
        "query_text": "AI healthcare",
        "content_type": "article",
        "limit": 10,
        "min_score": 0.1
    }
    
    article_response = await async_client.post("/search/", json=article_query)
    assert article_response.status_code == 200
    article_results = article_response.json()
    assert all(r["content_type"] == "article" for r in article_results)

async def test_search_by_topic(async_client: AsyncClient):
    """Test searching content by topic."""
    await create_test_data(async_client)
    
    response = await async_client.get("/search/topic/AI Healthcare")
    assert response.status_code == 200
    results = response.json()
    
    assert "scientific_studies" in results
    assert "articles" in results
    assert len(results["scientific_studies"]) > 0
    assert len(results["articles"]) > 0
    
    # Test with content type filter
    study_response = await async_client.get(
        "/search/topic/AI Healthcare",
        params={"content_type": "scientific_study"}
    )
    assert study_response.status_code == 200
    study_results = study_response.json()
    assert "articles" not in study_results
    assert len(study_results["scientific_studies"]) > 0

async def test_search_recent_content(async_client: AsyncClient):
    """Test searching recent content."""
    await create_test_data(async_client)
    
    response = await async_client.get(
        "/search/recent",
        params={"days": 7}
    )
    assert response.status_code == 200
    results = response.json()
    
    assert "scientific_studies" in results
    assert "articles" in results
    
    # Verify content is recent
    current_time = datetime.utcnow()
    for study in results["scientific_studies"]:
        study_date = datetime.fromisoformat(study["publication_date"])
        assert (current_time - study_date).days <= 7
    
    for article in results["articles"]:
        article_date = datetime.fromisoformat(article["publication_date"])
        assert (current_time - article_date).days <= 7

async def test_find_related_content(async_client: AsyncClient):
    """Test finding related content."""
    # Create data and get an article ID
    await create_test_data(async_client)
    
    # Get an AI healthcare article
    search_response = await async_client.post(
        "/articles/search",
        params={"query_text": "AI healthcare"}
    )
    article = search_response.json()[0]["content"]
    article_id = article["id"]
    
    # Find related content
    response = await async_client.get(
        f"/search/related/article/{article_id}",
        params={"limit": 5}
    )
    assert response.status_code == 200
    results = response.json()
    
    assert "scientific_studies" in results
    assert "articles" in results
    
    # Verify related content is relevant
    for study in results["scientific_studies"]:
        assert "AI" in study["title"] or "Healthcare" in study["title"]
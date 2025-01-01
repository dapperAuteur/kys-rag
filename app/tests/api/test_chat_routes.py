# app/tests/api/test_chat_routes.py

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from datetime import datetime, timezone
from app.api.routers.chat import router
from app.models.chat import ChatMessage, ScientificStudyAnalysisRequest
from app.services.chat import chat_service
import logging

# Set up logging so we can see what's happening in our tests
logger = logging.getLogger(__name__)

# Create a test app that we'll use to test our routes
app = FastAPI()
app.include_router(router)

# This runs before each test to set up what we need
@pytest.fixture
async def client():
    """Create a test client that we can use to make requests."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

class TestScientificStudyAnalysis:
    """Tests for analyzing scientific studies.
    
    These tests check that we can ask questions about studies
    and get helpful answers back.
    """
    
    async def test_successful_analysis(self, client):
        """Test getting analysis for a valid study."""
        # Send a question about a study
        response = await client.post(
            "/chat/scientific-studies/123",
            json={"question": "What were the main findings?"}
        )
        
        # Check that everything worked
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "findings" in data
        assert isinstance(data["findings"]["key_points"], list)
    
    async def test_missing_study(self, client):
        """Test what happens when we can't find the study."""
        response = await client.post(
            "/chat/scientific-studies/999",
            json={"question": "What were the findings?"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    async def test_invalid_question(self, client):
        """Test what happens with a bad question."""
        # Send a question that's too short
        response = await client.post(
            "/chat/scientific-studies/123",
            json={"question": "Why?"}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "question" in data["detail"][0]["loc"]

class TestArticleAnalysis:
    """Tests for analyzing news articles.
    
    These tests verify that we can check scientific claims
    made in news articles.
    """
    
    async def test_successful_analysis(self, client):
        """Test analyzing a valid article."""
        response = await client.post(
            "/chat/articles/123",
            json={"question": "Are the claims supported by science?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "claims" in data
        assert isinstance(data["claims"], list)
    
    async def test_missing_article(self, client):
        """Test what happens when we can't find the article."""
        response = await client.post(
            "/chat/articles/999",
            json={"question": "What claims does it make?"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

class TestChatMessages:
    """Tests for saving and retrieving chat messages.
    
    These tests check that we can save messages and get
    chat history when needed.
    """
    
    async def test_save_message(self, client):
        """Test saving a new chat message."""
        message_data = {
            "content_id": "123",
            "content_type": "scientific_study",
            "message": "This is a test message"
        }
        
        response = await client.post("/chat/messages", json=message_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message_id" in data
    
    async def test_get_chat_history(self, client):
        """Test getting chat history for a study."""
        # First save a message
        message_data = {
            "content_id": "123",
            "content_type": "scientific_study",
            "message": "Test message"
        }
        await client.post("/chat/messages", json=message_data)
        
        # Then try to get the history
        response = await client.get(
            "/chat/history/scientific_study/123",
            params={"limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    async def test_invalid_content_type(self, client):
        """Test what happens with an invalid content type."""
        response = await client.get(
            "/chat/history/invalid_type/123",
            params={"limit": 10}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "content type" in data["detail"].lower()

class TestIntegrationScenarios:
    """Tests for complete user scenarios.
    
    These tests check that different parts of our system
    work together correctly.
    """
    
    async def test_analyze_and_chat(self, client):
        """Test analyzing a study and then chatting about it."""
        # First analyze the study
        analysis_response = await client.post(
            "/chat/scientific-studies/123",
            json={"question": "What were the findings?"}
        )
        assert analysis_response.status_code == 200
        
        # Then save a message about it
        message_data = {
            "content_id": "123",
            "content_type": "scientific_study",
            "message": "The findings are interesting"
        }
        message_response = await client.post(
            "/chat/messages",
            json=message_data
        )
        assert message_response.status_code == 200
        
        # Finally get the chat history
        history_response = await client.get(
            "/chat/history/scientific_study/123"
        )
        assert history_response.status_code == 200
        assert len(history_response.json()) > 0
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.models.models import ChatMessage
from app.services.services import chat_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/scientific-studies/{study_id}", response_model=Dict[str, Any])
async def analyze_scientific_study(study_id: str, question: str):
    """Analyze a scientific study based on a question."""
    try:
        analysis = await chat_service.analyze_scientific_study(
            study_id=study_id,
            question=question
        )
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing scientific study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/articles/{article_id}", response_model=Dict[str, Any])
async def analyze_article(article_id: str, question: str):
    """Analyze an article based on a question."""
    try:
        analysis = await chat_service.analyze_article(
            article_id=article_id,
            question=question
        )
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages", response_model=str)
async def save_chat_message(message: ChatMessage):
    """Save a chat message."""
    try:
        message_id = await chat_service.save_message(message)
        return message_id
    except Exception as e:
        logger.error(f"Error saving chat message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{content_type}/{content_id}", response_model=List[ChatMessage])
async def get_chat_history(
    content_type: str,
    content_id: str,
    limit: int = Query(default=50, ge=1, le=200)
):
    """Get chat history for a specific content item."""
    try:
        if content_type not in ["scientific_study", "article"]:
            raise HTTPException(status_code=400, detail="Invalid content type")
            
        history = await chat_service.get_chat_history(
            content_id=content_id,
            content_type=content_type,
            limit=limit
        )
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
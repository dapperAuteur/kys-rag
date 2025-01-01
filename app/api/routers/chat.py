from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.models.models import ChatMessage
from app.services.services import chat_service
import logging
from app.models.chat import (
    ScientificStudyAnalysisRequest,
    ScientificStudyAnalysisResponse,
    ArticleAnalysisRequest,
    ArticleAnalysisResponse,
    ChatHistoryRequest,
    SaveMessageRequest,
    SaveMessageResponse
)
from app.services.services import chat_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/scientific-studies/{study_id}", response_model=ScientificStudyAnalysisResponse,
    description="Analyze a scientific study based on a question",
    responses={
        404: {"description": "Study not found"},
        422: {"description": "Invalid question format"},
        500: {"description": "Server error during analysis"}
    }
)
async def analyze_scientific_study(
    study_id: str,
    request: ScientificStudyAnalysisRequest
) -> ScientificStudyAnalysisResponse:
    """Analyze a scientific study based on a question.
    This endpoint processes questions about scientific studies and returns
    structured analysis including key findings, methodology, and relevant sections.
    
    Args:
        study_id: The ID of the scientific study to analyze
        request: The analysis request containing the question
        
    Returns:
        A structured analysis of the study based on the question
        
    Raises:
        HTTPException: If the study is not found or analysis fails
    """
    try:
        analysis = await chat_service.analyze_scientific_study(
            study_id=study_id,
            question=request.question
        )

        # Convert the analysis to our response model
        return ScientificStudyAnalysisResponse(
            title=analysis["title"],
            findings={
                "key_points": analysis.get("key_findings", []),
                "methodology": analysis.get("methodology"),
                "limitations": analysis.get("limitations", []),
                "citation": analysis.get("citation", "")
            },
            relevant_section=analysis.get("relevant_section"),
            confidence_score=analysis.get("confidence_score", 0.0),
            metadata=analysis.get("metadata", {})
        )
    except ValueError as e:
        logger.error(f"Study not found or invalid request: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing scientific study: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing the study: {str(e)})"
        )

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
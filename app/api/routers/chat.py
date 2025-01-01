from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from app.models.models import ChatMessage
from app.services.chat import chat_service
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

# Set up logging to help us track what's happening

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
    responses={
        500: {"description": "Internal server error"},
        404: {"description": "Resource not found"},
        400: {"description": "Bad request"}
    }
)

# Helper function to validate content type
def validate_content_type(content_type: str) -> str:
    """Make sure we're working with a valid content type."""
    valid_types = ["scientific_study", "article"]
    if content_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Content type must be one of: {', '.join(valid_types)}"
        )
    return content_type

@router.post("/scientific-studies/{study_id}", response_model=ScientificStudyAnalysisResponse,
    summary="Analyze a scientific study",
    description="Ask questions about a scientific study and get structured analysis"
)
async def analyze_scientific_study(
    study_id: str,
    request: ScientificStudyAnalysisRequest
) -> ScientificStudyAnalysisResponse:
    """
    Analyze a scientific study based on a question.
    This endpoint processes questions about scientific studies and returns
    structured analysis including key findings, methodology, and relevant sections.
    Get insights about a scientific study by asking questions.
    
    Args:
        study_id: The ID of the study you want to analyze
        request: Your question and any other analysis parameters
        
    Returns:
        A detailed analysis including key findings and relevant sections
        
    Raises:
        404: If we can't find the study
        500: If something goes wrong during analysis
    """
    logger.info(f"Analyzing scientific study {study_id}")
    try:
        # Try to analyze the study
        analysis = await chat_service.analyze_scientific_study(
            study_id=study_id,
            question=request.question
        )

         # Log success and return the analysis
        logger.info(f"Successfully analyzed study {study_id}")
        return ScientificStudyAnalysisResponse(**analysis)
        # return ScientificStudyAnalysisResponse(
        #     title=analysis["title"],
        #     findings={
        #         "key_points": analysis.get("key_findings", []),
        #         "methodology": analysis.get("methodology"),
        #         "limitations": analysis.get("limitations", []),
        #         "citation": analysis.get("citation", "")
        #     },
        #     relevant_section=analysis.get("relevant_section"),
        #     confidence_score=analysis.get("confidence_score", 0.0),
        #     metadata=analysis.get("metadata", {})
        # )
    except ValueError as e:
        # Log and handle missing study error
        logger.error(f"Study not found: {study_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Log and handle unexpected errors
        logger.error(f"Error analyzing scientific study: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing the study: {str(e)})"
        )

@router.post(
    "/articles/{article_id}",
    response_model=ArticleAnalysisResponse,
    summary="Analyze an article",
    description="Ask questions about an article and verify its scientific claims"
)
async def analyze_article(
    article_id: str,
    request: ArticleAnalysisRequest
) -> ArticleAnalysisResponse:
    """
    Analyze an article and verify its scientific claims.
    
    Args:
        article_id: The ID of the article to analyze
        request: Your question about the article
        
    Returns:
        Analysis including verified claims and scientific support
        
    Raises:
        404: If we can't find the article
        500: If something goes wrong during analysis
    """
    logger.info(f"Analyzing article {article_id}")
    try:
        # Try to analyze the article
        analysis = await chat_service.analyze_article(
            article_id=article_id,
            question=request.question
        )
        
        # Log success and return the analysis
        logger.info(f"Successfully analyzed article {article_id}")
        return ArticleAnalysisResponse(**analysis)
        
    except ValueError as e:
        # Log and handle missing article error
        logger.error(f"Article not found: {article_id}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing article: {e}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while analyzing the article"
        )

@router.post(
    "/messages",
    response_model=SaveMessageResponse,
    summary="Save a chat message",
    description="Save a message to the chat history"
)
async def save_chat_message(
    request: SaveMessageRequest
) -> SaveMessageResponse:
    """
    Save a message to our chat history.
    
    Args:
        request: The message to save and its details
        
    Returns:
        Confirmation that the message was saved
        
    Raises:
        500: If we can't save the message
    """
    logger.info("Saving new chat message")
    try:
         # Validate the content type
        validate_content_type(request.content_type)
        
        # Create a chat message from the request
        message = ChatMessage(
            content_id=request.content_id,
            content_type=request.content_type,
            message=request.message,
            user_id=request.user_id
        )
        
        # Try to save the message
        message_id = await chat_service.save_message(message)
        
        # Log success and return confirmation
        logger.info(f"Successfully saved message {message_id}")
        return SaveMessageResponse(message_id=message_id)
        
    except Exception as e:
        # Log and handle any errors
        logger.error(f"Error saving message: {e}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while saving your message"
        )

@router.get(
    "/history/{content_type}/{content_id}",
    response_model=List[ChatMessage],
    summary="Get chat history",
    description="Get the chat history for a specific article or study"
)
async def get_chat_history(
    content_type: str,
    content_id: str,
    limit: int = Query(default=50, ge=1, le=200)
)-> List[ChatMessage]:
    """
    Get the chat history for an article or study.
    
    Args:
        content_type: Either 'scientific_study' or 'article'
        content_id: The ID of the content you want history for
        limit: How many messages to return (max 200)
        
    Returns:
        List of chat messages in order
        
    Raises:
        400: If the content type is invalid
        500: If we can't get the history
    """
    logger.info(f"Getting chat history for {content_type} {content_id}")
    try:
        # Validate the content type
        validate_content_type(content_type)
        
        # Try to get the chat history
        history = await chat_service.get_chat_history(
            content_id=content_id,
            content_type=content_type,
            limit=limit
        )
        
        # Log success and return the history
        logger.info(f"Successfully retrieved chat history")
        return history
        
    except Exception as e:
        # Log and handle any errors
        logger.error(f"Error getting chat history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while getting the chat history"
        )
# app/models/responses/chat.py

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# Set up logging to help us track what's happening
logger = logging.getLogger(__name__)

class BaseResponse(BaseModel):
    """Every response will include these basic fields.
    
    This is like a template that all our other responses will use.
    It makes sure every response has:
    - A status message (success or error)
    - A timestamp showing when the response was created
    - Any extra information we might want to include
    """
    status: str = Field(
        default="success",
        description="Whether the request succeeded or failed"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this response was created"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Any extra information about the response"
    )
    
    @validator('status')
    def status_must_be_valid(cls, v):
        """Make sure status is either 'success' or 'error'"""
        valid_statuses = ['success', 'error']
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
        return v

class FindingsResponse(BaseModel):
    """The important parts we found in a scientific study.
    
    This organizes the key information we extract from a study into
    clear sections that are easy to understand.
    """
    key_points: List[str] = Field(
        default_factory=list,
        description="The main things the study discovered"
    )
    methodology: Optional[str] = Field(
        None,
        description="How the study was done"
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Things that might limit the study's conclusions"
    )
    citation: str = Field(
        ...,  # This means it's required
        description="How to reference this study"
    )

class ScientificStudyAnalysisResponse(BaseResponse):
    """What we send back when someone asks about a scientific study.
    
    This takes our findings and wraps them in a nice package with
    all the information someone might need to understand the study.
    """
    content_type: str = Field(
        default="scientific_study",
        const=True,
        description="The type of content we analyzed"
    )
    title: str = Field(
        ...,
        description="The title of the study"
    )
    findings: FindingsResponse = Field(
        ...,
        description="What we found in the study"
    )
    relevant_section: Optional[str] = Field(
        None,
        description="The part of the study that answers the question"
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How confident we are in our analysis (0-1)"
    )

class ClaimResponse(BaseModel):
    """Information about a claim made in an article.
    
    This helps us track whether claims in articles are supported
    by scientific evidence.
    """
    text: str = Field(
        ...,
        description="What the article claimed"
    )
    verified: bool = Field(
        ...,
        description="Whether we found scientific support for this claim"
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How confident we are about verification (0-1)"
    )
    verification_notes: Optional[str] = Field(
        None,
        description="Extra information about our verification"
    )

class ArticleAnalysisResponse(BaseResponse):
    """What we send back when someone asks about an article.
    
    This organizes our analysis of an article, including whether its
    claims are supported by scientific evidence.
    """
    content_type: str = Field(
        default="article",
        const=True,
        description="The type of content we analyzed"
    )
    title: str = Field(
        ...,
        description="The title of the article"
    )
    source: str = Field(
        ...,
        description="Where the article was published"
    )
    publication_date: datetime = Field(
        ...,
        description="When the article was published"
    )
    claims: List[ClaimResponse] = Field(
        default_factory=list,
        description="Claims made in the article and their verification"
    )
    scientific_support: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Scientific studies that support or dispute the article"
    )
    relevant_section: Optional[str] = Field(
        None,
        description="The part of the article that answers the question"
    )

class ChatMessageResponse(BaseResponse):
    """What we send back when saving a chat message.
    
    This confirms that we saved the message and includes
    details about when and where it was saved.
    """
    message_id: str = Field(
        ...,
        description="The ID of the saved message"
    )

class ErrorResponse(BaseModel):
    """What we send back when something goes wrong.
    
    This helps users understand what went wrong and how
    they might fix it.
    """
    status: str = Field(
        default="error",
        const=True,
        description="Indicates this is an error response"
    )
    code: int = Field(
        ...,
        description="The HTTP status code"
    )
    message: str = Field(
        ...,
        description="What went wrong"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="More information about the error"
    )

    class Config:
        """Extra settings for this model."""
        schema_extra = {
            "example": {
                "status": "error",
                "code": 404,
                "message": "We couldn't find that study",
                "details": {
                    "study_id": "123",
                    "suggestion": "Please check the ID and try again"
                }
            }
        }
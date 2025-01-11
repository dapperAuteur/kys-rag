# app/models/chat.py

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import PyObjectId

class ScientificStudyAnalysisRequest(BaseModel):
    """Request model for analyzing a scientific study.
    
    This model validates that questions are properly formed and not empty.
    The min_length ensures we don't process trivially short questions,
    while max_length prevents extremely long queries that might cause processing issues.
    """
    question: str = Field(
        ...,  # This means the field is required
        min_length=10,
        max_length=1000,
        description="The question to ask about the scientific study"
    )
    
    @validator('question')
    def validate_question_content(cls, v):
        """Ensure the question is meaningful and properly formatted."""
        if not any(word in v.lower() for word in ['what', 'why', 'how', 'where', 'when', 'who']):
            raise ValueError("Question should be a meaningful inquiry about the study")
        return v.strip()

class ArticleAnalysisRequest(BaseModel):
    """Request model for analyzing an article.
    
    Similar to ScientificStudyAnalysisRequest but potentially with different validation rules
    specific to article-related questions.
    """
    question: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="The question to ask about the article"
    )
    
    @validator('question')
    def validate_question_content(cls, v):
        """Ensure the question is meaningful and properly formatted."""
        if not any(word in v.lower() for word in ['what', 'why', 'how', 'where', 'when', 'who']):
            raise ValueError("Question should be a meaningful inquiry about the article")
        return v.strip()

class ScientificStudyFindings(BaseModel):
    """Model for representing study findings in the analysis."""
    key_points: List[str]
    methodology: Optional[str]
    limitations: List[str]
    citation: str

class ScientificStudyAnalysisResponse(BaseModel):
    """Response model for scientific study analysis.
    
    This model provides a structured way to return analysis results, including
    metadata about the study and the analysis process.
    """
    status: str = "success"
    content_type: str = "scientific_study"
    title: str
    findings: ScientificStudyFindings
    relevant_section: Optional[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ArticleClaim(BaseModel):
    """Model for representing verified claims from an article."""
    text: str
    verified: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    verification_notes: Optional[str]

class ArticleAnalysisResponse(BaseModel):
    """Response model for article analysis.
    
    This model structures the response to include both the article's claims
    and their verification status.
    """
    status: str = "success"
    content_type: str = "article"
    title: str
    source: str
    publication_date: datetime
    claims: List[ArticleClaim]
    scientific_support: List[Dict[str, str]]
    relevant_section: Optional[str]
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatHistoryRequest(BaseModel):
    """Request model for retrieving chat history.
    
    This model ensures proper pagination and filtering of chat history.
    """
    limit: int = Field(default=50, ge=1, le=200)
    before_timestamp: Optional[datetime] = None
    content_type: str = Field(...)
    
    @validator('content_type')
    def validate_content_type(cls, v):
        """Ensure content type is valid."""
        valid_types = ["scientific_study", "article"]
        if v not in valid_types:
            raise ValueError(f"Content type must be one of: {', '.join(valid_types)}")
        return v

class SaveMessageRequest(BaseModel):
    """Request model for saving chat messages.
    
    This model ensures all required message data is provided and validates
    the content format.
    """
    content_id: PyObjectId
    content_type: str
    message: str = Field(..., min_length=1, max_length=2000)
    user_id: Optional[str] = None
    
    @validator('content_type')
    def validate_content_type(cls, v):
        """Ensure content type is valid."""
        valid_types = ["scientific_study", "article"]
        if v not in valid_types:
            raise ValueError(f"Content type must be one of: {', '.join(valid_types)}")
        return v

class SaveMessageResponse(BaseModel):
    """Response model for message saving confirmation."""
    status: str = "success"
    message_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Type aliases for improved code readability
ScientificStudyAnalysis = Dict[str, Any]  # TODO: Replace with proper type
ArticleAnalysis = Dict[str, Any]  # TODO: Replace with proper type

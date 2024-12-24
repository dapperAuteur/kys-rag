from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator
from typing import List, Optional, Dict, Union, Any
from datetime import datetime
from bson import ObjectId
from enum import Enum

class PydanticObjectId(str):
    """Custom type for handling MongoDB ObjectIds with validation"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(str(value)):
            raise ValueError("Invalid ObjectId")
        return str(value)

class Author(BaseModel):
    """Author information with validation"""
    name: str = Field(..., min_length=1)
    email: Optional[EmailStr] = None
    institution: Optional[str] = None

class SourceType(str, Enum):
    """Types of content sources we handle"""
    SCIENTIFIC_STUDY = "scientific_study"
    ARTICLE = "article"

class Source(BaseModel):
    """Base model for content sources with type discrimination"""
    type: SourceType
    url: Optional[HttpUrl] = None
    pdf_path: Optional[str] = None
    title: str = Field(..., min_length=1)
    authors: List[Author]
    text_chunks: List[Dict[str, Union[str, List[float]]]] = Field(default_factory=list)

class TextChunk(BaseModel):
    """Represents a chunk of text with its vector embedding"""
    text: str = Field(..., min_length=1)
    vector: Optional[List[float]] = None
    
    @validator('vector')
    def validate_vector_dimensions(cls, v):
        if v is not None and len(v) != 768:  # SciBERT dimensions
            raise ValueError("Vector must have 768 dimensions")
        return v

class Study(BaseModel):
    """Scientific study model with metadata and source information"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    source: Source
    discipline: Optional[str] = None
    publication_date: Optional[datetime] = None
    keywords: List[str] = Field(default_factory=list)
    citation_count: Optional[int] = Field(default=0, ge=0)
    doi: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class Article(BaseModel):
    """Article model that references scientific studies"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    source: Source
    cited_studies: List[PydanticObjectId] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class SearchQuery(BaseModel):
    """Search parameters with validation"""
    query_text: str = Field(..., min_length=1)
    content_type: str = Field("all", pattern="^(study|article|all)$")
    limit: int = Field(default=10, ge=1, le=100)
    min_score: float = Field(default=0.5, ge=0, le=1.0)
    discipline: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_citations: Optional[int] = Field(default=None, ge=0)
    keywords: Optional[List[str]] = None

class SearchResponse(BaseModel):
    """Search response with study and score"""
    study: Study
    score: float = Field(..., ge=0, le=1.0)

class StatusResponse(BaseModel):
    """API response status with details"""
    status: str = Field(..., pattern="^(success|error)$")
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
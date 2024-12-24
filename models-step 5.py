from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId

class PydanticObjectId(str):
    """Custom type for handling MongoDB ObjectIds"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(str(v)):
            raise ValueError("Invalid ObjectId")
        return str(v)

class Author(BaseModel):
    """Represents an author of a scientific study"""
    name: str
    email: Optional[EmailStr] = None
    institution: Optional[str] = None

class Citation(BaseModel):
    """Represents a citation to a scientific study"""
    doi: Optional[str] = None
    url: Optional[HttpUrl] = None
    title: str
    authors: List[str]
    publication_date: Optional[datetime] = None
    verified: bool = False

class Article(BaseModel):
    """Represents a web article discussing scientific studies"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    url: HttpUrl
    title: str
    text: str
    cited_studies: List[Citation]
    vector: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    verified: bool = False

    class Config:
        populate_by_name = True

class Study(BaseModel):
    """Represents a scientific study with enhanced metadata"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    text: str
    topic: str
    discipline: str
    vector: Optional[List[float]] = None
    source_type: str = "pdf"  # pdf or web
    source_url: Optional[HttpUrl] = None
    
    # Metadata fields
    authors: List[Author]
    publication_date: Optional[datetime] = None
    keywords: List[str] = Field(default_factory=list)
    citation_count: int = 0
    doi: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    chunks: List[Dict[str, any]] = Field(default_factory=list)

    class Config:
        populate_by_name = True

class SearchQuery(BaseModel):
    """Enhanced search query parameters with metadata filtering"""
    query_text: str
    limit: int = 10
    min_score: float = 0.5
    discipline: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_citations: Optional[int] = None
    keywords: Optional[List[str]] = None

class ChatMessage(BaseModel):
    """Represents a message in the chat system"""
    role: str  # user or assistant
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    """Represents a chat session"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    messages: List[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class StatusResponse(BaseModel):
    """API response status"""
    status: str
    message: str
    details: dict = {}
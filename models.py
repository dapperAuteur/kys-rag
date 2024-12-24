from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
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

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Smith",
                "email": "jane.smith@university.edu",
                "institution": "University Research Center"
            }
        }

class Study(BaseModel):
    """Represents a scientific study with enhanced metadata"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    text: str
    topic: str
    discipline: str
    vector: Optional[List[float]] = None
    
    # Metadata fields
    authors: List[Author]
    publication_date: Optional[datetime] = None
    keywords: List[str] = Field(default_factory=list)
    citation_count: int = 0
    doi: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "AI in Healthcare",
                "text": "A study about artificial intelligence applications in healthcare",
                "topic": "AI Healthcare",
                "discipline": "Computer Science",
                "authors": [
                    {
                        "name": "Jane Smith",
                        "email": "jane.smith@university.edu",
                        "institution": "University Research Center"
                    }
                ],
                "keywords": ["AI", "healthcare", "machine learning"],
                "doi": "10.1234/example.doi",
                "citation_count": 0
            }
        }

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

    class Config:
        json_schema_extra = {
            "example": {
                "query_text": "artificial intelligence healthcare",
                "limit": 10,
                "discipline": "Computer Science",
                "date_from": "2024-01-01T00:00:00Z",
                "min_citations": 5,
                "keywords": ["AI", "healthcare"]
            }
        }

class SearchResponse(BaseModel):
    """Search result with metadata and similarity score"""
    study: Study
    score: float

class StatusResponse(BaseModel):
    """API response status"""
    status: str
    message: str
    details: dict = {}
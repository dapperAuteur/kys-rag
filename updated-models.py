from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List, Optional, Dict, Union
from datetime import datetime
from bson import ObjectId

class PydanticObjectId(str):
    """Custom type for handling MongoDB ObjectIds with updated validation"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, info):
        """Updated validator to match Pydantic's validation signature"""
        if not isinstance(value, (str, ObjectId)):
            raise TypeError('ObjectId required')
        if not ObjectId.is_valid(str(value)):
            raise ValueError('Invalid ObjectId')
        return str(value)

class Author(BaseModel):
    """Represents an author"""
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

class ScientificStudy(BaseModel):
    """Represents a scientific study"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    text: str
    topic: str
    discipline: str
    pdf_path: Optional[str] = None
    doi: Optional[str] = None
    vector: Optional[List[float]] = None
    authors: List[Author]
    publication_date: Optional[datetime] = None
    citation_count: int = 0
    text_chunks: List[Dict[str, Union[str, List[float]]]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Effects of Exercise on Brain Function",
                "text": "Research study on cognitive benefits of exercise",
                "topic": "Neuroscience",
                "discipline": "Biology",
                "pdf_path": "papers/exercise_study.pdf",
                "authors": [{"name": "Dr. Jane Smith"}],
                "doi": "10.1234/example.doi"
            }
        }

class Article(BaseModel):
    """Represents an article that cites scientific studies"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    text: str
    url: HttpUrl
    topic: str
    publication_date: Optional[datetime] = None
    authors: List[Author]
    cited_studies: List[PydanticObjectId] = Field(default_factory=list)
    text_chunks: List[Dict[str, Union[str, List[float]]]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "New Research Shows Exercise Boosts Brain Power",
                "text": "Article discussing recent exercise studies",
                "url": "https://example.com/article",
                "topic": "Health",
                "authors": [{"name": "John Writer"}],
                "cited_studies": ["507f1f77bcf86cd799439011"]
            }
        }

class SearchQuery(BaseModel):
    """Search parameters"""
    query_text: str
    limit: int = 10
    min_score: float = 0.5
    content_type: str = "all"  # "study", "article", or "all"
    discipline: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_citations: Optional[int] = None

class SearchResponse(BaseModel):
    """Search result with metadata and similarity score"""
    content_type: str  # "study" or "article"
    study: Optional[ScientificStudy] = None
    article: Optional[Article] = None
    score: float

class StatusResponse(BaseModel):
    """API response status"""
    status: str
    message: str
    details: dict = {}
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import List, Optional, Dict, Union
from datetime import datetime
from bson import ObjectId
from enum import Enum

class PydanticObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(str(v)):
            raise ValueError("Invalid ObjectId")
        return str(v)

class Author(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    institution: Optional[str] = None

class SourceType(str, Enum):
    SCIENTIFIC_STUDY = "scientific_study"
    ARTICLE = "article"

class Source(BaseModel):
    type: SourceType
    url: Optional[HttpUrl] = None
    pdf_path: Optional[str] = None
    title: str
    authors: List[Author]
    publication_date: Optional[datetime] = None
    citations: List[PydanticObjectId] = Field(default_factory=list)
    text_chunks: List[Dict[str, Union[str, List[float]]]] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "scientific_study",
                "url": "https://example.com/study.pdf",
                "title": "Example Study",
                "authors": [{"name": "Jane Smith"}],
                "publication_date": "2024-01-01T00:00:00Z"
            }
        }

class Study(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    text: str
    topic: str
    discipline: str
    vector: Optional[List[float]] = None
    source: Source
    authors: List[Author]
    publication_date: Optional[datetime] = None
    keywords: List[str] = Field(default_factory=list)
    citation_count: int = 0
    doi: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class SearchQuery(BaseModel):
    query_text: str
    limit: int = 10
    min_score: float = 0.5
    source_type: Optional[SourceType] = None
    discipline: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_citations: Optional[int] = None
    keywords: Optional[List[str]] = None

class SearchResponse(BaseModel):
    study: Study
    score: float

class StatusResponse(BaseModel):
    status: str
    message: str
    details: dict = {}
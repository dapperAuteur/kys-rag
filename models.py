from pydantic import BaseModel, Field
from typing import List, Optional
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

class Study(BaseModel):
    """Represents a scientific study"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    text: str
    topic: str
    discipline: str
    vector: Optional[List[float]] = None

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "AI in Healthcare",
                "text": "A study about artificial intelligence applications in healthcare",
                "topic": "AI Healthcare",
                "discipline": "Computer Science"
            }
        }

class SearchQuery(BaseModel):
    """Search query parameters"""
    query_text: str
    limit: int = 10
    min_score: float = 0.5

class SearchResponse(BaseModel):
    """Search result with similarity score"""
    study: Study
    score: float

class StatusResponse(BaseModel):
    """API response status"""
    status: str
    message: str
    details: dict = {}
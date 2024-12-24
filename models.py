from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

class PydanticObjectId(str):
    """Custom type for handling MongoDB ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, (str, ObjectId)):
            raise ValueError("Invalid ObjectId")
        return str(v)

class Study(BaseModel):
    """Model representing a scientific study"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    text: str
    topic: str
    discipline: str
    vector: List[float] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        arbitrary_types_allowed=True
    )

class SearchQuery(BaseModel):
    """Model for search requests"""
    query_text: str
    limit: int = Field(default=5, ge=1, le=100)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)

class SearchResponse(BaseModel):
    """Model for search responses"""
    study: Study
    score: float

class StatusResponse(BaseModel):
    """Model for status responses"""
    status: str
    message: str
    details: Optional[dict] = None
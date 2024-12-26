from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import BeforeValidator
from typing import List, Optional, Any, Annotated
from bson import ObjectId

# Custom type for handling MongoDB ObjectId
def validate_object_id(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str):
        try:
            return str(ObjectId(v))
        except Exception:
            raise ValueError("Invalid ObjectId format")
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]

class Study(BaseModel):
    """Represents a scientific study"""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "title": "AI in Healthcare",
                "text": "A study about artificial intelligence applications in healthcare",
                "topic": "AI Healthcare",
                "discipline": "Computer Science"
            }
        }
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    title: str
    text: str
    topic: str
    discipline: str
    vector: Optional[List[float]] = None

class SearchQuery(BaseModel):
    """Search query parameters"""
    model_config = ConfigDict(populate_by_name=True)
    
    query_text: str
    limit: int = Field(default=10, ge=1, le=100)
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)

class SearchResponse(BaseModel):
    """Search result with similarity score"""
    model_config = ConfigDict(populate_by_name=True)
    
    study: Study
    score: float = Field(ge=0.0, le=1.0)

class StatusResponse(BaseModel):
    """API response status"""
    model_config = ConfigDict(populate_by_name=True)
    
    status: str
    message: str
    details: dict = Field(default_factory=dict)
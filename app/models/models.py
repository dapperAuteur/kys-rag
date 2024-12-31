from pydantic import BaseModel, Field, ConfigDict, HttpUrl, validator
from pydantic.functional_validators import BeforeValidator
from typing import List, Optional, Any, Dict, Annotated
from bson import ObjectId
from datetime import datetime, timezone
import logging

# Set up logging to help us track what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom type for handling MongoDB ObjectId
def validate_object_id(v: Any) -> str:
    """Convert different types of input to a valid ObjectId string"""
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str):
        try:
            return str(ObjectId(v))
        except Exception:
            raise ValueError("Invalid ObjectId format")
    raise ValueError("Invalid ObjectId")

PyObjectId = Annotated[str, BeforeValidator(validate_object_id)]

def ensure_utc_datetime(value: Any) -> datetime:
    """Convert various datetime inputs to UTC datetime objects"""
    logger.info(f"Processing datetime value: {value} of type {type(value)}")
    
    if isinstance(value, datetime):
        # If datetime has no timezone, assume UTC
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value
    elif isinstance(value, str):
        # Handle different string formats
        try:
            # Replace 'Z' with '+00:00' for ISO format compatibility
            if value.endswith('Z'):
                value = value[:-1] + '+00:00'
            dt = datetime.fromisoformat(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError as e:
            logger.error(f"Date parsing error: {e}")
            raise ValueError("Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS+00:00)")
    raise ValueError("Value must be a datetime object or ISO format string")

class BaseDocument(BaseModel):
    """Base document with common fields"""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    title: str
    text: str
    topic: str
    vector: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ScientificStudy(BaseDocument):
    """Represents a scientific research paper or study"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "AI in Healthcare",
                "text": "A study about artificial intelligence applications in healthcare",
                "authors": ["John Doe", "Jane Smith"],
                "publication_date": "2024-01-15T00:00:00Z",
                "journal": "Nature",
                "doi": "10.1234/example.doi",
                "topic": "AI Healthcare",
                "discipline": "Computer Science"
            }
        }
    )
    
    authors: List[str]
    publication_date: datetime
    journal: str
    doi: Optional[str] = None
    discipline: str
    citations: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    peer_reviewed: bool = Field(default=True)

class Claim(BaseModel):
    """Represents a scientific claim made in an article"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    text: str
    related_scientific_study_ids: List[PyObjectId] = Field(default_factory=list)
    confidence_score: Optional[float] = None
    verified: bool = False
    verification_notes: Optional[str] = None
    context: Optional[str] = None
    location_in_text: Optional[Dict[str, int]] = None  # start and end positions
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None

class Article(BaseDocument):
    """Represents a news article or blog post"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "New AI Breakthrough in Medical Diagnosis",
                "text": "Article about recent developments in AI-powered medical diagnosis",
                "author": "John Journalist",
                "publication_date": "2024-01-20T00:00:00Z",
                "source_url": "https://example.com/article",
                "publication_name": "Tech News Daily",
                "topic": "AI Healthcare"
            }
        }
    )
    
    author: str
    publication_date: datetime
    source_url: HttpUrl
    publication_name: str
    related_scientific_studies: List[PyObjectId] = Field(default_factory=list)
    claims: List[Claim] = Field(default_factory=list)
    article_type: str = Field(default="news")  # news, blog, opinion, etc.
    credibility_score: Optional[float] = None

class SearchQuery(BaseModel):
    """Search query parameters"""
    model_config = ConfigDict(populate_by_name=True)
    
    query_text: str
    limit: int = Field(default=10, ge=1, le=100)
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)
    content_type: Optional[str] = Field(
        default=None, 
        description="Filter by 'scientific_study' or 'article'"
    )

class SearchResponse(BaseModel):
    """Search result with similarity score"""
    model_config = ConfigDict(populate_by_name=True)
    
    content: Any  # Can be either ScientificStudy or Article
    score: float = Field(ge=0.0, le=1.0)
    content_type: str  # "scientific_study" or "article"

class ChatMessage(BaseModel):
    """Represents a message in the chat history"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    content_id: PyObjectId  # ID of the scientific study or article being discussed
    content_type: str  # "scientific_study" or "article"
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    references: List[PyObjectId] = Field(default_factory=list)  # Referenced scientific studies/articles

class ArticleCreate(BaseModel):
    """Model for creating a new article with enhanced URL and date handling"""
    title: str
    text: str
    author: str
    publication_date: datetime
    source_url: HttpUrl
    publication_name: str
    topic: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "New Research Findings",
                "text": "Article content here...",
                "author": "John Doe",
                "publication_date": "2024-01-20T00:00:00+00:00",
                "source_url": "https://example.com/article",
                "publication_name": "Science Daily",
                "topic": "Medical Research"
            }
        }
    )

    @validator('publication_date', pre=True)
    def validate_date(cls, v):
        """Validate and convert date to UTC datetime"""
        return ensure_utc_datetime(v)
    
    def model_dump(self, **kwargs):
        """Custom dump method to convert HttpUrl to string"""
        data = super().model_dump(**kwargs)
        # Convert HttpUrl to string for MongoDB storage
        if 'source_url' in data:
            data['source_url'] = str(data['source_url'])
        return data

class ArticleResponse(BaseModel):
    """Model for article response with enhanced date handling"""
    id: str
    title: str
    text: str
    author: str
    publication_date: datetime
    source_url: HttpUrl
    publication_name: str
    topic: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            ObjectId: str
        }
    )

    @validator('publication_date', 'created_at', 'updated_at', pre=True)
    def validate_dates(cls, v):
        """Ensure all dates are proper UTC datetime objects"""
        return ensure_utc_datetime(v)

class StatusResponse(BaseModel):
    """API response status"""
    model_config = ConfigDict(populate_by_name=True)
    
    status: str
    message: str
    details: dict = Field(default_factory=dict)
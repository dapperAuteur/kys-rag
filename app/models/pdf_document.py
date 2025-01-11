# app/models/pdf_document.py

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Union, Any
from datetime import datetime
from .models import PyObjectId, BaseDocument

class PDFDocument(BaseDocument):
    """
    Represents a PDF document in the system.
    
    This model stores both the extracted content and metadata from PDFs,
    along with relationships to scientific studies or articles.
    """
    
    # File information
    original_filename: str
    file_size: int
    md5_hash: str = Field(..., description="MD5 hash of the file for uniqueness checking")
    
    # Content
    extracted_text: str = Field(..., description="Full text extracted from the PDF")
    page_count: int = Field(ge=1)
    
    # Metadata from PDF - Now accepts multiple value types
    pdf_metadata: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict,
        description="Metadata extracted from the PDF file"
    )
    
    # Relationships
    scientific_study_id: Optional[PyObjectId] = None
    article_id: Optional[PyObjectId] = None
    
    # Processing information
    processing_status: str = Field(
        default="pending",
        description="Status of PDF processing: pending, processing, completed, failed"
    )
    processing_error: Optional[str] = None
    processed_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Example Scientific Paper",
                "original_filename": "paper.pdf",
                "file_size": 1048576,  # 1MB
                "md5_hash": "d41d8cd98f00b204e9800998ecf8427e",
                "extracted_text": "Content of the paper...",
                "page_count": 10,
                "pdf_metadata": {
                    "author": "John Doe",
                    "creation_date": "2024-01-10T12:00:00",
                    "page_count": 10
                }
            }
        }
    
    @validator('processing_status')
    def validate_status(cls, v):
        """Ensure processing status is valid."""
        valid_statuses = {'pending', 'processing', 'completed', 'failed'}
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v

class PDFUploadResponse(BaseModel):
    """Response model for PDF upload endpoint."""
    document_id: str
    status: str
    message: str
    details: Dict[str, Union[str, int, float, bool, None]] = Field(
        default_factory=dict,
        description="Dictionary containing additional response details"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "507f1f77bcf86cd799439011",
                "status": "success",
                "message": "PDF processed and stored successfully",
                "details": {
                    "title": "Example Document",
                    "page_count": 10,
                    "processing_status": "completed"
                }
            }
        }

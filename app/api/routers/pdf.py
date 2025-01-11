# app/api/routers/pdf.py

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Dict, Optional
import logging
from app.services.pdf_processor import pdf_processor
from app.services.pdf_document_service import pdf_document_service
from app.models.models import StatusResponse
from app.models.pdf_document import PDFDocument, PDFUploadResponse
import tempfile
import os
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pdf", tags=["PDF Processing"])

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    scientific_study_id: Optional[str] = Form(None),
    article_id: Optional[str] = Form(None)
):
    """
    Upload and process a PDF file, storing its content in the database.
    
    Args:
        file: The uploaded PDF file
        scientific_study_id: Optional ID of related scientific study
        article_id: Optional ID of related article
        
    Returns:
        PDFUploadResponse with document ID and status
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        logger.info(f"Processing PDF upload: {file.filename}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            # Write uploaded file to temp file
            content = await file.read()
            tmp_file.write(content)
        
        try:
            # Process and store the PDF
            document = await pdf_document_service.process_and_store_pdf(
                tmp_path,
                file.filename,
                scientific_study_id,
                article_id
            )
            
            return PDFUploadResponse(
                document_id=str(document.id),
                status="success",
                message="PDF processed and stored successfully",
                details={
                    "title": document.title,
                    "page_count": document.page_count,
                    "processing_status": document.processing_status
                }
            )
            
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}", response_model=PDFDocument)
async def get_pdf_document(document_id: str):
    """
    Retrieve a PDF document by ID.
    
    Args:
        document_id: ID of the PDF document
        
    Returns:
        PDFDocument instance
    """
    try:
        document = await pdf_document_service.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="PDF document not found")
        return document
    except Exception as e:
        logger.error(f"Error retrieving PDF document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}/link/study/{study_id}", response_model=StatusResponse)
async def link_to_study(document_id: str, study_id: str):
    """
    Link a PDF document to a scientific study.
    
    Args:
        document_id: ID of the PDF document
        study_id: ID of the scientific study
        
    Returns:
        Status response indicating success or failure
    """
    try:
        success = await pdf_document_service.link_to_scientific_study(
            document_id,
            study_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Document or study not found")
            
        return StatusResponse(
            status="success",
            message="PDF linked to scientific study successfully",
            details={
                "document_id": document_id,
                "study_id": study_id
            }
        )
    except Exception as e:
        logger.error(f"Error linking PDF to study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{document_id}/link/article/{article_id}", response_model=StatusResponse)
async def link_to_article(document_id: str, article_id: str):
    """
    Link a PDF document to an article.
    
    Args:
        document_id: ID of the PDF document
        article_id: ID of the article
        
    Returns:
        Status response indicating success or failure
    """
    try:
        success = await pdf_document_service.link_to_article(
            document_id,
            article_id
        )
        if not success:
            raise HTTPException(status_code=404, detail="Document or article not found")
            
        return StatusResponse(
            status="success",
            message="PDF linked to article successfully",
            details={
                "document_id": document_id,
                "article_id": article_id
            }
        )
    except Exception as e:
        logger.error(f"Error linking PDF to article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract-text", response_model=StatusResponse)
async def extract_text_from_pdf(file: UploadFile = File(...)):
    """
    Extract text content from an uploaded PDF file.
    
    Args:
        file: The uploaded PDF file
        
    Returns:
        StatusResponse with extracted text in details
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        logger.info(f"Processing PDF upload: {file.filename}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            # Write uploaded file to temp file
            content = await file.read()
            tmp_file.write(content)
        
        try:
            # Process the PDF
            text = await pdf_processor.extract_text(tmp_path)
            
            return StatusResponse(
                status="success",
                message="Text extracted successfully",
                details={
                    "filename": file.filename,
                    "text": text,
                    "character_count": len(text)
                }
            )
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metadata", response_model=StatusResponse)
async def get_pdf_metadata(file: UploadFile = File(...)):
    """
    Extract metadata from an uploaded PDF file.
    
    Args:
        file: The uploaded PDF file
        
    Returns:
        StatusResponse with metadata in details
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        logger.info(f"Extracting metadata from PDF: {file.filename}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            # Write uploaded file to temp file
            content = await file.read()
            tmp_file.write(content)
        
        try:
            # Extract metadata
            metadata = await pdf_processor.get_metadata(tmp_path)
            
            return StatusResponse(
                status="success",
                message="Metadata extracted successfully",
                details={
                    "filename": file.filename,
                    "metadata": metadata
                }
            )
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Error extracting metadata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=StatusResponse)
async def analyze_pdf(file: UploadFile = File(...)):
    """
    Perform full analysis of a PDF file (both text and metadata).
    
    Args:
        file: The uploaded PDF file
        
    Returns:
        StatusResponse with both text and metadata in details
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        logger.info(f"Analyzing PDF: {file.filename}")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            # Write uploaded file to temp file
            content = await file.read()
            tmp_file.write(content)
        
        try:
            # Extract both text and metadata
            text = await pdf_processor.extract_text(tmp_path)
            metadata = await pdf_processor.get_metadata(tmp_path)
            
            return StatusResponse(
                status="success",
                message="PDF analysis completed successfully",
                details={
                    "filename": file.filename,
                    "text": text,
                    "metadata": metadata,
                    "character_count": len(text)
                }
            )
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except Exception as e:
        logger.error(f"Error analyzing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

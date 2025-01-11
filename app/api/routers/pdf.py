# app/api/routers/pdf.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import logging
from app.services.pdf_processor import pdf_processor
from app.models.models import StatusResponse
import tempfile
import os
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pdf", tags=["PDF Processing"])

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

# app/services/pdf_processor.py

from typing import Dict, Optional, List, Union
import logging
from pathlib import Path
import PyPDF2
import pdfplumber
from datetime import datetime
from app.core.config import get_settings

logger = logging.getLogger(__name__)

class PDFProcessor:
    """Handles all PDF processing operations including text extraction and metadata parsing."""

    def __init__(self):
        """Initialize the PDF processor with configuration settings."""
        self.settings = get_settings()
        logger.info("Initialized PDFProcessor")

    async def extract_text(self, file_path: Union[str, Path]) -> str:
        """
        Extract text content from a PDF file using pdfplumber.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content as a string
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is corrupted or invalid PDF
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"PDF file not found: {file_path}")
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            logger.info(f"Starting text extraction from: {file_path}")
            text_content = []
            
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"Processing {total_pages} pages")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.debug(f"Processing page {page_num}/{total_pages}")
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                    else:
                        logger.warning(f"No text extracted from page {page_num}")

            full_text = "\n\n".join(text_content)
            logger.info(f"Successfully extracted {len(full_text)} characters")
            return full_text

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise ValueError(f"Failed to process PDF: {str(e)}")

    async def get_metadata(self, file_path: Union[str, Path]) -> Dict[str, str]:
        """
        Extract metadata from PDF file using PyPDF2.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If metadata extraction fails
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"PDF file not found: {file_path}")
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        try:
            logger.info(f"Extracting metadata from: {file_path}")
            metadata = {}
            
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                doc_info = reader.metadata
                
                if doc_info:
                    # Standard metadata fields
                    metadata_fields = [
                        'title', 'author', 'subject', 'creator', 
                        'producer', 'keywords'
                    ]
                    
                    for field in metadata_fields:
                        value = doc_info.get(f'/{field.capitalize()}')
                        if value:
                            metadata[field] = str(value)

                    # Extract creation and modification dates
                    if doc_info.get('/CreationDate'):
                        metadata['creation_date'] = self._parse_pdf_date(
                            doc_info['/CreationDate']
                        )
                    if doc_info.get('/ModDate'):
                        metadata['modification_date'] = self._parse_pdf_date(
                            doc_info['/ModDate']
                        )

                    # Add page count
                    metadata['page_count'] = len(reader.pages)
                    
                    logger.info(f"Successfully extracted metadata: {list(metadata.keys())}")
                else:
                    logger.warning("No metadata found in PDF")
                    metadata['warning'] = 'No metadata available'

            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            raise ValueError(f"Failed to extract metadata: {str(e)}")

    def _parse_pdf_date(self, date_str: str) -> Optional[str]:
        """
        Parse PDF date format into ISO format.
        
        Args:
            date_str: Date string from PDF metadata
            
        Returns:
            ISO formatted date string or None if parsing fails
        """
        try:
            # Remove 'D:' prefix and timezone if present
            date_str = date_str.replace('D:', '')[:14]
            # Parse into datetime object
            date_obj = datetime.strptime(date_str, '%Y%m%d%H%M%S')
            return date_obj.isoformat()
        except Exception as e:
            logger.warning(f"Failed to parse date {date_str}: {e}")
            return None

# Create singleton instance
pdf_processor = PDFProcessor()

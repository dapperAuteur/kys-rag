# app/services/pdf_document_service.py

import hashlib
from typing import Optional, Dict, Any
import logging
from datetime import datetime
from pathlib import Path
from app.models.pdf_document import PDFDocument
from app.core.database import Collection, database
from .base import BaseService
from .pdf_processor import pdf_processor
from .section_detector import section_detector
from bson import ObjectId

logger = logging.getLogger(__name__)

class PDFDocumentService(BaseService[PDFDocument]):
    """Service for managing PDF documents in the database."""
    
    def __init__(self):
        """Initialize the PDF document service."""
        super().__init__(Collection.PDF_DOCUMENTS, PDFDocument)
        logger.info("Initialized PDFDocumentService")
    
    async def process_and_store_pdf(
        self,
        file_path: Path,
        original_filename: str,
        scientific_study_id: Optional[str] = None,
        article_id: Optional[str] = None
    ) -> PDFDocument:
        """
        Process a PDF file and store its content in the database.
        
        This function handles the entire lifecycle of processing a PDF:
            - Calculating file hash to detect duplicates
            - Extracting text and metadata
            - Determining document topic
            - Storing the processed document

        Args:
            file_path: Path to the PDF file
            original_filename: Original name of the uploaded file
            scientific_study_id: Optional ID of related scientific study
            article_id: Optional ID of related article
            
        Returns:
            Created PDFDocument instance
            
        Raises:
            ValueError: If file processing fails
        """
        try:
            logger.info(f"Processing PDF: {original_filename}")
            
            # Calculate file hash and size
            md5_hash = await self._calculate_file_hash(file_path)
            file_size = file_path.stat().st_size
            
            # Check for duplicate by hash
            existing_doc = await self._find_by_hash(md5_hash)
            if existing_doc:
                logger.info(f"Found existing PDF document: {existing_doc.id}")
                return existing_doc
            
            # Extract text and metadata
            text = await pdf_processor.extract_text(file_path)
            metadata = await pdf_processor.get_metadata(file_path)

            # Extract sections and tables
            sections = await section_detector.find_sections(text)
            tables = await section_detector.extract_tables(text)

            # Determine topic from filename or metadata
            topic = self._determine_topic(metadata, original_filename)
            # if topic == 'uncategorized' and 'keywords' in metadata:
            #     topic = metadata['keywords'].split(',')[0].strip()
            
            # Get page count from metadata or set default
            page_count = metadata.get('page_count', 1)
            if isinstance(page_count, str):
                try:
                    page_count = int(page_count)
                except ValueError:
                    page_count = 1
            if page_count < 1:
                page_count = 1  # Ensure at least 1 page

            # Remove page_count from metadata since we store it separately
            if 'page_count' in metadata:
                del metadata['page_count']
            
            # Create document
            document = PDFDocument(
                title=metadata.get('title', original_filename),
                text=text,  # Add the extracted text
                topic=topic,  # Add the topic
                original_filename=original_filename,
                file_size=file_size,
                md5_hash=md5_hash,
                extracted_text=text,
                page_count=page_count,
                pdf_metadata=metadata,
                sections=sections,
                tables=tables,
                scientific_study_id=ObjectId(scientific_study_id) if scientific_study_id else None,
                article_id=ObjectId(article_id) if article_id else None,
                processing_status="completed",
                processed_at=datetime.utcnow()
            )
            
            # Store in database
            document_id = await self.create(document)
            logger.info(f"Stored PDF document with ID: {document_id}")
            
            # Get and return the stored document
            return await self.get_by_id(document_id)
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            # Create document with error status
            error_doc = PDFDocument(
                title=original_filename,
                text="Error processing document",  # Add required text
                topic="error",  # Add required topic
                original_filename=original_filename,
                file_size=file_path.stat().st_size,
                md5_hash=await self._calculate_file_hash(file_path),
                extracted_text="",
                page_count=1, # Set minimum valid page count,
                pdf_metadata={},
                processing_status="failed",
                processing_error=str(e),
                processed_at=datetime.utcnow()
            )
            await self.create(error_doc)
            raise ValueError(f"Failed to process PDF: {str(e)}")
        
    def _determine_topic(self, metadata: Dict[str, Any], filename: str) -> str:
        """
        Determine the document topic from metadata or filename.
        
        This helper function tries multiple approaches to find a meaningful topic:
        1. Use the subject from metadata
        2. Use keywords from metadata
        3. Use the filename as a fallback
        """
        # Try to get topic from subject
        topic = metadata.get('subject')
        if topic:
            return topic.strip()
        
        # Try to get topic from keywords
        keywords = metadata.get('keywords')
        if keywords:
            # Take the first keyword if available
            if isinstance(keywords, str):
                return keywords.split(',')[0].strip()
            return str(keywords)
        
        # Use filename as fallback, removing extension and common separators
        base_name = Path(filename).stem
        cleaned_name = base_name.replace('_', ' ').replace('-', ' ')
        return cleaned_name.strip()
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                md5.update(chunk)
        return md5.hexdigest()
    
    async def _find_by_hash(self, md5_hash: str) -> Optional[PDFDocument]:
        """Find a document by its MD5 hash."""
        coll = await self.get_collection()
        doc = await coll.find_one({'md5_hash': md5_hash})
        return PDFDocument(**doc) if doc else None
    
    async def link_to_scientific_study(
        self,
        document_id: str,
        study_id: str
    ) -> bool:
        """Link PDF document to a scientific study."""
        try:
            coll = await self.get_collection()
            result = await coll.update_one(
                {'_id': ObjectId(document_id)},
                {
                    '$set': {
                        'scientific_study_id': ObjectId(study_id),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error linking to scientific study: {e}")
            raise
    
    async def link_to_article(
        self,
        document_id: str,
        article_id: str
    ) -> bool:
        """Link PDF document to an article."""
        try:
            coll = await self.get_collection()
            result = await coll.update_one(
                {'_id': ObjectId(document_id)},
                {
                    '$set': {
                        'article_id': ObjectId(article_id),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error linking to article: {e}")
            raise

# Create singleton instance
pdf_document_service = PDFDocumentService()

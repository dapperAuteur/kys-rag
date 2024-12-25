# services.py

from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Optional, Dict, Any, Union
import logging
from datetime import datetime
from models import (
    Study, Article, SearchQuery, SearchResponse, TextChunk, 
    Source, PydanticObjectId, Author
)
from database import database
from config import get_settings
from bson import ObjectId
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import re
from urllib.parse import urlparse
import tempfile

# Configure logging
logger = logging.getLogger(__name__)

class ContentService:
    """Base service for content processing with vector embeddings."""
    
    def __init__(self):
        """Initialize SciBERT model and tokenizer."""
        try:
            logger.info("Initializing ContentService...")
            self.settings = get_settings()
            
            logger.info(f"Loading model: {self.settings.MODEL_NAME}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.settings.MODEL_NAME)
            self.model = AutoModel.from_pretrained(self.settings.MODEL_NAME)
            
            logger.info("ContentService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ContentService: {e}")
            raise

    async def process_source(self, source: Source) -> List[Dict[str, Any]]:
        """Extract and process text from source, returning chunks with embeddings."""
        try:
            if source.url:
                text = await self._extract_text_from_url(source.url)
            elif source.pdf_path:
                text = await self._extract_text_from_pdf(source.pdf_path)
            else:
                raise ValueError("Source must have either URL or PDF path")
                
            chunks = self._chunk_text(
                text, 
                self.settings.CHUNK_SIZE, 
                self.settings.CHUNK_OVERLAP
            )
            return await self._process_chunks(chunks)
        except Exception as e:
            logger.error(f"Error processing source: {e}")
            raise

    async def _extract_text_from_url(self, url: str) -> str:
        """Extract text content from URL with PDF handling."""
        try:
            response = requests.get(str(url))
            response.raise_for_status()
            
            if url.lower().endswith('.pdf'):
                with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
                    tmp.write(response.content)
                    return await self._extract_text_from_pdf(tmp.name)
                    
            soup = BeautifulSoup(response.text, 'html.parser')
            for element in soup(['script', 'style', 'nav']):
                element.decompose()
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            logger.error(f"Error extracting text from URL: {e}")
            raise

    async def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file."""
        try:
            text = ""
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        start = 0
        
        while start < len(words):
            end = start + chunk_size
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            start = start + chunk_size - overlap
            
        return chunks

    async def _process_chunks(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """Generate embeddings for text chunks."""
        processed_chunks = []
        
        for chunk in chunks:
            embedding = await self.generate_embedding(chunk)
            processed_chunks.append({
                "text": chunk,
                "vector": embedding
            })
            
        return processed_chunks

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for text using SciBERT."""
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
                return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

class StudyService(ContentService):
    """Service for managing scientific studies."""
    
    async def create_study(self, study: Study) -> str:
        """Create new study with processed content."""
        try:
            # Process source content
            study.source.text_chunks = await self.process_source(study.source)
            
            # Prepare for MongoDB
            document = study.model_dump(by_alias=True, exclude_none=True)
            if "_id" in document and document["_id"] is None:
                del document["_id"]

            # Insert into database
            result = await database.db.studies.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating study: {e}")
            raise

    async def get_study(self, study_id: str) -> Optional[Study]:
        """Retrieve study by ID."""
        try:
            document = await database.db.studies.find_one(
                {"_id": ObjectId(study_id)}
            )
            return Study(**document) if document else None
        except Exception as e:
            logger.error(f"Error retrieving study: {e}")
            raise

class ArticleService(ContentService):
    """Service for managing articles."""
    
    async def create_article(self, article: Article) -> str:
        """Create new article with processed content."""
        try:
            # Process source content
            article.source.text_chunks = await self.process_source(article.source)
            
            # Prepare for MongoDB
            document = article.model_dump(by_alias=True, exclude_none=True)
            if "_id" in document and document["_id"] is None:
                del document["_id"]

            # Insert into database
            result = await database.db.articles.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating article: {e}")
            raise

    async def get_article(self, article_id: str) -> Optional[Article]:
        """Retrieve article by ID."""
        try:
            document = await database.db.articles.find_one(
                {"_id": ObjectId(article_id)}
            )
            return Article(**document) if document else None
        except Exception as e:
            logger.error(f"Error retrieving article: {e}")
            raise

class SearchService(ContentService):
    """Service for searching studies and articles."""
    
    async def search(self, query: SearchQuery) -> List[SearchResponse]:
        """Search for content based on query parameters."""
        try:
            query_vector = await self.generate_embedding(query.query_text)
            
            # Build search pipeline
            pipeline = self._build_search_pipeline(query_vector, query)
            
            # Execute search
            results = await database.vector_similarity_search(
                query_vector=query_vector,
                limit=query.limit,
                metadata_filters=self._build_metadata_filters(query)
            )
            
            # Format results
            return [
                SearchResponse(
                    study=Study(**doc) if doc.get("source_type") == "study" 
                    else Article(**doc),
                    score=doc.get("score", 0.0)
                )
                for doc in results
                if doc.get("score", 0.0) >= query.min_score
            ]
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            raise

    def _build_metadata_filters(self, query: SearchQuery) -> Dict[str, Any]:
        """Build metadata filters for search query."""
        filters = {}
        
        if query.content_type != "all":
            filters["source.type"] = query.content_type
            
        if query.discipline:
            filters["discipline"] = query.discipline
            
        if query.date_from or query.date_to:
            date_filter = {}
            if query.date_from:
                date_filter["$gte"] = query.date_from
            if query.date_to:
                date_filter["$lte"] = query.date_to
            filters["publication_date"] = date_filter
            
        return filters

# Initialize service instances
study_service = StudyService()
article_service = ArticleService()
search_service = SearchService()

from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Optional, Dict, Any
import logging
from models import Study, SearchQuery, SearchResponse, Source, SourceType
from database import database
from config import get_settings
from bson import ObjectId
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import re
from urllib.parse import urlparse
import tempfile

logger = logging.getLogger(__name__)

class StudyService:
    def __init__(self):
        self.settings = get_settings()
        self.tokenizer = AutoTokenizer.from_pretrained(self.settings.MODEL_NAME)
        self.model = AutoModel.from_pretrained(self.settings.MODEL_NAME)
        
    async def process_source(self, source: Source) -> List[Dict[str, Any]]:
        """Process source content and generate chunks with embeddings"""
        if source.url:
            text = await self._extract_text_from_url(source.url)
        elif source.pdf_path:
            text = await self._extract_text_from_pdf(source.pdf_path)
        else:
            raise ValueError("Source must have either URL or PDF path")
            
        chunks = self._chunk_text(text, chunk_size=512, overlap=50)
        return await self._process_chunks(chunks)

    async def _extract_text_from_url(self, url: str) -> str:
        """Extract text content from URL"""
        try:
            response = requests.get(str(url))
            response.raise_for_status()
            
            if url.lower().endswith('.pdf'):
                with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
                    tmp.write(response.content)
                    return await self._extract_text_from_pdf(tmp.name)
                    
            soup = BeautifulSoup(response.text, 'html.parser')
            # Remove scripts, styles, and navigation
            for element in soup(['script', 'style', 'nav']):
                element.decompose()
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            logger.error(f"Error extracting text from URL: {e}")
            raise

    async def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF"""
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
        """Split text into overlapping chunks"""
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
        """Process chunks and generate embeddings"""
        processed_chunks = []
        
        for chunk in chunks:
            embedding = await self.generate_embedding(chunk)
            processed_chunks.append({
                "text": chunk,
                "vector": embedding
            })
            
        return processed_chunks

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for text"""
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

    async def save_study(self, study: Study) -> str:
        """Save study with processed source content"""
        try:
            # Process source content
            study.source.text_chunks = await self.process_source(study.source)
            
            # Convert to dictionary for MongoDB
            document = study.model_dump(by_alias=True, exclude_none=True)
            
            # Remove id if None
            if "_id" in document and document["_id"] is None:
                del document["_id"]

            # Insert into database
            result = await database.db.studies.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving study: {e}")
            raise

    async def search_similar_studies(
        self,
        query: SearchQuery
    ) -> List[SearchResponse]:
        """Search for similar studies using vector similarity"""
        try:
            query_vector = await self.generate_embedding(query.query_text)
            
            pipeline = self._build_search_pipeline(query_vector, query)
            results = await database.vector_similarity_search(pipeline=pipeline)
            
            response_results = []
            for doc in results:
                score = doc.pop("score", 0.0)
                if score >= query.min_score:
                    study = Study(**doc)
                    response_results.append(SearchResponse(study=study, score=score))
            
            return response_results
        except Exception as e:
            logger.error(f"Error searching studies: {e}")
            raise

    def _build_search_pipeline(self, query_vector: List[float], query: SearchQuery) -> List[Dict]:
        """Build MongoDB aggregation pipeline for search"""
        pipeline = []
        
        # Vector search stage
        if database.vector_search_enabled:
            pipeline.append({
                "$search": {
                    "index": "vector_index",
                    "knnBeta": {
                        "vector": query_vector,
                        "path": "source.text_chunks.vector",
                        "k": query.limit * 2
                    }
                }
            })
        
        # Metadata filters
        match_stage = {}
        
        if query.source_type:
            match_stage["source.type"] = query.source_type
            
        if query.discipline:
            match_stage["discipline"] = query.discipline
            
        if query.date_from or query.date_to:
            date_filter = {}
            if query.date_from:
                date_filter["$gte"] = query.date_from
            if query.date_to:
                date_filter["$lte"] = query.date_to
            match_stage["publication_date"] = date_filter
            
        if query.min_citations is not None:
            match_stage["citation_count"] = {"$gte": query.min_citations}
            
        if query.keywords:
            match_stage["keywords"] = {"$all": query.keywords}
            
        if match_stage:
            pipeline.append({"$match": match_stage})
            
        # Limit results
        pipeline.append({"$limit": query.limit})
        
        return pipeline

study_service = StudyService()
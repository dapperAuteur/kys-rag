from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Optional, Dict, Any
import logging
from models import Study, SearchQuery, SearchResponse, Article, Citation
from database import database
from config import get_settings
from bson import ObjectId
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup
import httpx
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles processing of PDFs and web articles"""
    
    def __init__(self):
        self.settings = get_settings()
        
    async def process_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF"""
        try:
            text = extract_text(file_content)
            return text.strip()
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
            
    async def process_url(self, url: str) -> Dict[str, Any]:
        """Fetch and process web article"""
        async with httpx.AsyncClient(timeout=self.settings.REQUEST_TIMEOUT) as client:
            headers = {"User-Agent": self.settings.USER_AGENT}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract main content (customize based on site structure)
            content = ""
            article_body = soup.find('article') or soup.find(class_=re.compile(r'article|content|post'))
            if article_body:
                content = article_body.get_text(strip=True)
            else:
                content = soup.get_text(strip=True)
                
            title = soup.title.string if soup.title else ""
            
            return {
                "title": title,
                "text": content,
                "url": url
            }
            
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.settings.MAX_CHUNK_SIZE - self.settings.CHUNK_OVERLAP):
            chunk_words = words[i:i + self.settings.MAX_CHUNK_SIZE]
            chunk_text = " ".join(chunk_words)
            chunks.append({
                "text": chunk_text,
                "start_idx": i,
                "end_idx": i + len(chunk_words)
            })
            
        return chunks

class StudyService:
    """Handles business logic for study operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.tokenizer = AutoTokenizer.from_pretrained(self.settings.MODEL_NAME)
        self.model = AutoModel.from_pretrained(self.settings.MODEL_NAME)
        self.doc_processor = DocumentProcessor()
        
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

    async def process_pdf_study(self, file_content: bytes, metadata: Dict[str, Any]) -> str:
        """Process PDF study and store in database"""
        try:
            # Extract text from PDF
            text = await self.doc_processor.process_pdf(file_content)
            
            # Create chunks
            chunks = self.doc_processor.chunk_text(text)
            
            # Create study object
            study = Study(
                title=metadata.get("title", "Untitled Study"),
                text=text,
                topic=metadata.get("topic", "Unknown"),
                discipline=metadata.get("discipline", "Unknown"),
                authors=metadata.get("authors", []),
                doi=metadata.get("doi"),
                source_type="pdf",
                chunks=chunks
            )
            
            # Generate and add vector embedding
            study.vector = await self.generate_embedding(text)
            
            # Save to database
            study_id = await database.save_study(study)
            return study_id
            
        except Exception as e:
            logger.error(f"Error processing PDF study: {e}")
            raise

    async def process_article(self, article_data: Dict[str, Any]) -> str:
        """Process web article and its citations"""
        try:
            # Fetch and process article
            article_content = await self.doc_processor.process_url(article_data["url"])
            
            # Process cited studies
            citations = []
            for citation_url in article_data.get("cited_studies", []):
                try:
                    citation_content = await self.doc_processor.process_url(citation_url)
                    citation = Citation(
                        url=citation_url,
                        title=citation_content["title"],
                        authors=[],  # Would need more processing to extract authors
                        verified=False
                    )
                    citations.append(citation)
                except Exception as e:
                    logger.warning(f"Error processing citation {citation_url}: {e}")
                    continue
            
            # Create article object
            article = Article(
                url=article_data["url"],
                title=article_content["title"],
                text=article_content["text"],
                cited_studies=citations
            )
            
            # Generate and add vector embedding
            article.vector = await self.generate_embedding(article_content["text"])
            
            # Save to database
            article_id = await database.save_article(article)
            return article_id
            
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            raise

# Initialize
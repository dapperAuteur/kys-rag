from typing import List, Optional, Dict, Any
import logging
from app.core.database import Collection
from app.models.models import ChatMessage, Article, ScientificStudy
from datetime import datetime
from bson import ObjectId
from .article import article_service
from .scientific_study import scientific_study_service
from .claim import claim_service
from app.core.database import database

logger = logging.getLogger(__name__)

class ChatService:
    """Service for handling chat interactions."""
    
    def __init__(self):
        """Initialize the chat service."""
        self.settings = database.settings
    
    async def save_message(self, message: ChatMessage) -> str:
        """Save a chat message."""
        try:
            coll = await database.get_collection(Collection.CHAT_HISTORY)
            result = await coll.insert_one(message.model_dump())
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")
            raise

    async def get_chat_history(
        self,
        content_id: str,
        content_type: str,
        limit: int = 50
    ) -> List[ChatMessage]:
        """Get chat history for a specific content item."""
        try:
            coll = await database.get_collection(Collection.CHAT_HISTORY)
            cursor = coll.find({
                "content_id": ObjectId(content_id),
                "content_type": content_type
            }).sort("timestamp", -1).limit(limit)
            
            return [ChatMessage(**doc) async for doc in cursor]
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            raise

    async def analyze_scientific_study(
        self,
        study_id: str,
        question: str
    ) -> Dict[str, Any]:
        """Analyze a scientific study based on a question."""
        try:
            study = await scientific_study_service.get_by_id(study_id)
            if not study:
                raise ValueError("Scientific study not found")
            
            # Create a focused response about the study
            response = {
                "content_type": "scientific_study",
                "title": study.title,
                "key_findings": await self._extract_key_findings(study.text),
                "relevant_section": await self._find_relevant_section(study.text, question),
                "methodology": await self._extract_methodology(study.text),
                "limitations": await self._extract_limitations(study.text),
                "citation": f"{', '.join(study.authors)} ({study.publication_date.year}). {study.title}. {study.journal}."
            }
            
            return response
        except Exception as e:
            logger.error(f"Error analyzing scientific study: {e}")
            raise

    async def analyze_article(
        self,
        article_id: str,
        question: str
    ) -> Dict[str, Any]:
        """Analyze an article based on a question."""
        try:
            article = await article_service.get_by_id(article_id)
            if not article:
                raise ValueError("Article not found")
            
            # Get related scientific studies
            related_studies = await article_service.get_related_scientific_studies(
                article_id
            )
            
            # Extract and verify claims if not already done
            if not article.claims:
                article.claims = await claim_service.extract_claims(article.text)
                for claim in article.claims:
                    claim = await claim_service.process_claim(claim)
            
            # Create a comprehensive response
            response = {
                "content_type": "article",
                "title": article.title,
                "source": article.publication_name,
                "publication_date": article.publication_date,
                "claims": [
                    {
                        "text": claim.text,
                        "verified": claim.verified,
                        "confidence": claim.confidence_score,
                        "verification_notes": claim.verification_notes
                    }
                    for claim in article.claims
                ],
                "scientific_support": [
                    {
                        "title": study.title,
                        "journal": study.journal,
                        "doi": study.doi
                    }
                    for study in related_studies
                ],
                "relevant_section": await self._find_relevant_section(
                    article.text,
                    question
                )
            }
            
            return response
        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            raise

    async def _extract_key_findings(self, text: str) -> List[str]:
        """Extract key findings from text."""
        # Placeholder for more sophisticated extraction
        findings_section = text.lower().find("findings")
        if findings_section != -1:
            section_text = text[findings_section:findings_section + 1000]
            return [s.strip() for s in section_text.split('.') if len(s.strip()) > 20][:5]
        return []

    async def _extract_methodology(self, text: str) -> Optional[str]:
        """Extract methodology section from text."""
        # Placeholder for more sophisticated extraction
        methods_section = text.lower().find("methods")
        if methods_section != -1:
            return text[methods_section:methods_section + 500]
        return None

    async def _extract_limitations(self, text: str) -> List[str]:
        """Extract study limitations from text."""
        # Placeholder for more sophisticated extraction
        limitations_section = text.lower().find("limitations")
        if limitations_section != -1:
            section_text = text[limitations_section:limitations_section + 500]
            return [s.strip() for s in section_text.split('.') if "limitation" in s.lower()]
        return []

    async def _find_relevant_section(
        self,
        text: str,
        question: str
    ) -> Optional[str]:
        """Find the most relevant section of text for a question."""
        # Placeholder for more sophisticated relevance matching
        sentences = text.split('.')
        most_relevant = max(
            sentences,
            key=lambda s: len(set(s.lower().split()) & set(question.lower().split()))
        )
        return most_relevant if most_relevant else None

# Create singleton instance
chat_service = ChatService()
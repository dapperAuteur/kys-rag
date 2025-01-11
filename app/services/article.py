from typing import List, Optional, Dict, Any
import logging
from app.core.database import Collection, database  # Added database import
from app.models import Article, Claim, SearchResponse, ScientificStudy
from .base import BaseService
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)

class ArticleService(BaseService[Article]):
    """Service for handling news article and blog post operations."""
    
    def __init__(self):
        """Initialize the article service."""
        super().__init__(Collection.ARTICLES, Article)
    
    async def fetch_article_metadata(self, url: str) -> Dict[str, Any]:
        """Fetch metadata for an article from its URL."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (compatible; ScienceDecoderBot/1.0)"
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Find meta tags first to avoid repeated lookups
                        meta_description = soup.find("meta", {"name": "description"})
                        
                        # Extract metadata
                        metadata = {
                            "title": soup.title.string if soup.title else None,
                            "description": meta_description.get("content") if meta_description else None,
                            "author": (meta_author.get("content") if (meta_author := soup.find("meta", {"name": "author"})) else None),
                            "published_date": (meta_pub_date.get("content") if (meta_pub_date := soup.find("meta", {"property": "article:published_time"})) else None),
                            "modified_date": (meta_mod_date.get("content") if (meta_mod_date := soup.find("meta", {"property": "article:modified_time"})) else None),
                            "keywords": (meta_keywords.get("content") if (meta_keywords := soup.find("meta", {"name": "keywords"})) else None)
                        }
                        
                        return {k: v for k, v in metadata.items() if v is not None}
                    else:
                        logger.warning(f"Failed to fetch article metadata: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"Error fetching article metadata: {e}")
            return {}

    async def create_with_metadata(self, article: Article) -> str:
        """Create an article with additional metadata from URL."""
        metadata = await self.fetch_article_metadata(str(article.source_url))
        if metadata:
            # Update article with fetched metadata
            article.title = metadata.get("title", article.title)
            if "published_date" in metadata:
                article.publication_date = datetime.fromisoformat(metadata["published_date"])
            article.metadata.update({"scraped": metadata})
        
        return await self.create(article)

    async def add_claim(self, article_id: str, claim: Claim) -> bool:
        """Add a new claim to an article."""
        try:
            coll = await self.get_collection()
            result = await coll.update_one(
                {"_id": ObjectId(article_id)},
                {
                    "$push": {"claims": claim.model_dump()},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error adding claim: {e}")
            raise

    async def verify_claim(
        self,
        article_id: str,
        claim_index: int,
        verification_notes: str,
        confidence_score: float,
        verified: bool
    ) -> bool:
        """Update the verification status of a claim."""
        try:
            coll = await self.get_collection()
            result = await coll.update_one(
                {"_id": ObjectId(article_id)},
                {
                    "$set": {
                        f"claims.{claim_index}.verified": verified,
                        f"claims.{claim_index}.verification_notes": verification_notes,
                        f"claims.{claim_index}.confidence_score": confidence_score,
                        f"claims.{claim_index}.verified_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error verifying claim: {e}")
            raise

    async def link_scientific_study(self, article_id: str, study_id: str) -> bool:
        """Link a scientific study to an article."""
        try:
            coll = await self.get_collection()
            result = await coll.update_one(
                {"_id": ObjectId(article_id)},
                {
                    "$addToSet": {"related_scientific_studies": ObjectId(study_id)},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error linking scientific study: {e}")
            raise

    async def get_related_scientific_studies(
        self,
        article_id: str
    ) -> List[ScientificStudy]:
        """Get all scientific studies related to an article."""
        try:
            coll = await self.get_collection()
            article = await coll.find_one({"_id": ObjectId(article_id)})
            if not article or not article.get("related_scientific_studies"):
                return []
            
            scientific_studies_coll = await database.get_collection(
                Collection.SCIENTIFIC_STUDIES
            )
            
            cursor = scientific_studies_coll.find({
                "_id": {"$in": article["related_scientific_studies"]}
            })
            
            return [ScientificStudy(**doc) async for doc in cursor]
        except Exception as e:
            logger.error(f"Error getting related scientific studies: {e}")
            raise

    async def search_similar_articles(
        self,
        query_text: str,
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[SearchResponse]:
        """Search for similar articles using vector similarity."""
        try:
            results = await self.search_similar(query_text, limit, min_score)
            
            return [
                SearchResponse(
                    content=Article(**{k: v for k, v in doc.items() if k != "similarity"}),
                    score=doc["similarity"],
                    content_type="article"
                )
                for doc in results
            ]
        except Exception as e:
            logger.error(f"Error searching similar articles: {e}")
            raise

    # article.py
    async def search_by_topic(self, topic: str, limit: int = 10) -> List[Article]:
        """Search for articles by topic."""
        try:
            coll = await self.get_collection()
            cursor = coll.find({"topic": topic}).limit(limit)
            return [Article(**doc) async for doc in cursor]
        except Exception as e:
            logger.error(f"Error searching by topic: {e}")
            raise

# Create singleton instance
article_service = ArticleService()
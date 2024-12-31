from typing import List, Dict, Any, Optional
import logging
from app.models.models import SearchQuery, SearchResponse, ScientificStudy, Article
from .scientific_study import scientific_study_service
from .article import article_service
from datetime import datetime

logger = logging.getLogger(__name__)

class SearchService:
    """Service for handling cross-collection searches."""
    
    async def search_all(self, query: SearchQuery) -> List[SearchResponse]:
        """Search across all content types."""
        try:
            results = []
            
            # Filter by content type if specified
            if query.content_type == "scientific_study":
                results.extend(await self._search_scientific_studies(query))
            elif query.content_type == "article":
                results.extend(await self._search_articles(query))
            else:
                # Search both collections if no specific type is requested
                results.extend(await self._search_scientific_studies(query))
                results.extend(await self._search_articles(query))
            
            # Sort combined results by score
            results.sort(key=lambda x: x.score, reverse=True)
            
            # Apply limit to final results
            return results[:query.limit]
        except Exception as e:
            logger.error(f"Error performing cross-collection search: {e}")
            raise

    async def _search_scientific_studies(
        self,
        query: SearchQuery
    ) -> List[SearchResponse]:
        """Search scientific studies collection."""
        return await scientific_study_service.search_similar_studies(
            query_text=query.query_text,
            limit=query.limit,
            min_score=query.min_score
        )

    async def _search_articles(
        self,
        query: SearchQuery
    ) -> List[SearchResponse]:
        """Search articles collection."""
        return await article_service.search_similar_articles(
            query_text=query.query_text,
            limit=query.limit,
            min_score=query.min_score
        )

    async def search_by_topic(
        self,
        topic: str,
        content_type: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, List[Any]]:
        """Search for content by topic."""
        try:
            results = {}
            
            if content_type in [None, "scientific_study"]:
                scientific_studies = await scientific_study_service.search_by_topic(topic, limit)
                results["scientific_studies"] = scientific_studies
            
            if content_type in [None, "article"]:
                articles = await article_service.search_by_topic(topic, limit)
                results["articles"] = articles
            
            return results
        except Exception as e:
            logger.error(f"Error searching by topic: {e}")
            raise

    async def search_recent(
        self,
        days: int = 30,
        content_type: Optional[str] = None,
        limit: int = 10
    ) -> Dict[str, List[Any]]:
        """Search for recent content."""
        try:
            results = {}
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            if content_type in [None, "scientific_study"]:
                scientific_studies = await scientific_study_service.search_by_date(
                    after_date=cutoff_date,
                    limit=limit
                )
                results["scientific_studies"] = scientific_studies
            
            if content_type in [None, "article"]:
                articles = await article_service.search_by_date(
                    after_date=cutoff_date,
                    limit=limit
                )
                results["articles"] = articles
            
            return results
        except Exception as e:
            logger.error(f"Error searching recent content: {e}")
            raise

    async def find_related_content(
        self,
        content_id: str,
        content_type: str,
        limit: int = 5
    ) -> Dict[str, List[Any]]:
        """Find content related to a specific item."""
        try:
            if content_type == "scientific_study":
                study = await scientific_study_service.get_by_id(content_id)
                if not study:
                    raise ValueError("Scientific study not found")
                
                similar_studies = await scientific_study_service.search_similar_studies(
                    study.text,
                    limit=limit
                )
                articles = await article_service.search_similar_articles(
                    study.text,
                    limit=limit
                )
                
                return {
                    "scientific_studies": [s.content for s in similar_studies],
                    "articles": [a.content for a in articles]
                }
            
            elif content_type == "article":
                article = await article_service.get_by_id(content_id)
                if not article:
                    raise ValueError("Article not found")
                
                similar_articles = await article_service.search_similar_articles(
                    article.text,
                    limit=limit
                )
                studies = await scientific_study_service.search_similar_studies(
                    article.text,
                    limit=limit
                )
                
                return {
                    "articles": [a.content for a in similar_articles],
                    "scientific_studies": [s.content for s in studies]
                }
            
            else:
                raise ValueError(f"Invalid content type: {content_type}")
            
        except Exception as e:
            logger.error(f"Error finding related content: {e}")
            raise

# Create singleton instance
search_service = SearchService()
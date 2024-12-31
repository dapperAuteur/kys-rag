from typing import List, Optional, Dict, Any
import logging
from app.core.database import Collection
from app.models.models import ScientificStudy, SearchResponse
from .base import BaseService
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class ScientificStudyService(BaseService[ScientificStudy]):
    """Service for handling scientific study operations."""
    
    def __init__(self):
        """Initialize the scientific study service."""
        super().__init__(Collection.SCIENTIFIC_STUDIES, ScientificStudy)
    
    async def fetch_doi_metadata(self, doi: str) -> Dict[str, Any]:
        """Fetch metadata for a DOI from CrossRef API."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.crossref.org/works/{doi}"
                headers = {"Accept": "application/json"}
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["message"]
                    else:
                        logger.warning(f"Failed to fetch DOI metadata: {response.status}")
                        return {}
        except Exception as e:
            logger.error(f"Error fetching DOI metadata: {e}")
            return {}

    async def create_with_doi(self, study: ScientificStudy) -> str:
        """Create a scientific study with additional metadata from DOI."""
        if study.doi:
            metadata = await self.fetch_doi_metadata(study.doi)
            if metadata:
                # Update study with DOI metadata
                study.journal = metadata.get("container-title", [study.journal])[0]
                study.publication_date = datetime.fromisoformat(
                    metadata.get("published-print", {}).get("date-parts", [[""]])[0][0]
                )
                study.authors = [
                    f"{author.get('given', '')} {author.get('family', '')}"
                    for author in metadata.get("author", [])
                ]
                study.metadata.update({"crossref": metadata})
        
        return await self.create(study)

    async def search_by_discipline(
        self,
        discipline: str,
        limit: int = 10
    ) -> List[ScientificStudy]:
        """Search for scientific studies by discipline."""
        try:
            coll = await self.get_collection()
            cursor = coll.find({"discipline": discipline}).limit(limit)
            return [ScientificStudy(**doc) async for doc in cursor]
        except Exception as e:
            logger.error(f"Error searching by discipline: {e}")
            raise

    async def search_similar_studies(
        self,
        query_text: str,
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[SearchResponse]:
        """Search for similar scientific studies using vector similarity."""
        try:
            results = await self.search_similar(query_text, limit, min_score)
            
            return [
                SearchResponse(
                    content=ScientificStudy(**{k: v for k, v in doc.items() if k != "similarity"}),
                    score=doc["similarity"],
                    content_type="scientific_study"
                )
                for doc in results
            ]
        except Exception as e:
            logger.error(f"Error searching similar scientific studies: {e}")
            raise

    async def update_citations(
        self,
        study_id: str,
        citations: List[str]
    ) -> bool:
        """Update the citations for a scientific study."""
        try:
            coll = await self.get_collection()
            result = await coll.update_one(
                {"_id": study_id},
                {
                    "$set": {
                        "citations": citations,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating citations: {e}")
            raise

# Create singleton instance
scientific_study_service = ScientificStudyService()
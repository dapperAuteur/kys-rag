from typing import List, Optional, Dict, Any
import logging

from bson import ObjectId
from app.core.database import Collection
from app.models.models import ScientificStudy, SearchResponse
from app.models.pdf_document import PDFDocument
from .base import BaseService
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

class ScientificStudyService(BaseService[ScientificStudy]):
    """Service for handling scientific study operations."""
    
    def __init__(self):
        """Initialize the scientific study service."""
        super().__init__(Collection.SCIENTIFIC_STUDIES, ScientificStudy)
        self.collection_name = Collection.SCIENTIFIC_STUDIES
    
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
            raise HTTPException(
                status_code=500,
                detail="Could not complete search by discipline. Please try again."
            )

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
            raise HTTPException(
                status_code=500,
                detail="Could not complete search of similar scientific studies. Please try again."
            )

    async def update_citations(
        self,
        study_id: str,
        citations: List[str]
    ) -> bool:
        """Update the citations for a scientific study."""
        try:
            coll = await self.get_collection()
            result = await coll.update_one(
                {"_id": ObjectId(study_id)},
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

    async def create_with_sections(self, study: ScientificStudy) -> str:
        """Create study with section-level embeddings."""
        # Generate embeddings for each section
        for section_name, section_text in study.sections.items():
            embedding = await self.generate_embedding(section_text)
            study.section_embeddings[section_name] = embedding
            
        return await self.create(study)

    async def search_sections(
        self,
        query_text: str,
        section_type: str,
        limit: int = 10,
        min_score: float = 0.5
    ) -> List[SearchResponse]:
        """Search for similar sections across studies."""
        query_vector = await self.generate_embedding(query_text)
        
        pipeline = [
            {
                "$match": {
                    f"sections.{section_type}": {"$exists": True}
                }
            },
            {
            "$addFields": {
                "similarity": {
                    "$let": {
                        "vars": {
                            "dotProduct": {
                                "$reduce": {
                                    "input": {"$zip": {"inputs": [f"$section_embeddings.{section_type}", query_vector]}},
                                    "initialValue": 0.0,
                                    "in": {
                                        "$add": [
                                            "$$value",
                                            {"$multiply": [
                                                {"$arrayElemAt": ["$$this", 0]},
                                                {"$arrayElemAt": ["$$this", 1]}
                                            ]}
                                        ]
                                    }
                                }
                            }
                        },
                        "in": {"$min": [1.0, {"$max": [0.0, "$$dotProduct"]}]}
                    }
                }
            }
        },
            {"$match": {"similarity": {"$gte": min_score}}},
            {"$sort": {"similarity": -1}},
            {"$limit": limit}
        ]
        
        coll = await self.get_collection()
        results = await coll.aggregate(pipeline).to_list(length=limit)
        return [
            SearchResponse(
                content=ScientificStudy(**{k:v for k,v in doc.items() if k != "similarity"}),
                score=doc["similarity"],
                content_type="scientific_study"
            )
            for doc in results
        ]
    
    # app/services/scientific_study.py - Add section embeddings during creation

    async def create_from_pdf(self, pdf_document: PDFDocument) -> str:
        """Create scientific study with section embeddings from PDF."""
        try:
            # Generate embeddings for sections
            section_embeddings = {}
            for section_name, section_text in pdf_document.sections.items():
                embedding = await self.generate_embedding(section_text)
                section_embeddings[section_name] = embedding

            study = ScientificStudy(
                title=pdf_document.title,
                text=pdf_document.extracted_text,
                sections=pdf_document.sections,
                section_embeddings=section_embeddings,
                topic=pdf_document.topic,
                pdf_id=pdf_document.id
            )
            
            study_id = await self.create(study)
            logger.info(f"Created scientific study with ID: {study_id}")
            return study_id

        except Exception as e:
            logger.error(f"Error creating scientific study: {e}")
            raise

# Create singleton instance
scientific_study_service = ScientificStudyService()
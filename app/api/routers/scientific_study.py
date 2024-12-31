from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.models import ScientificStudy, SearchResponse, StatusResponse
from app.services import scientific_study_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scientific-studies", tags=["Scientific Studies"])

@router.post("/", response_model=StatusResponse)
async def create_scientific_study(study: ScientificStudy):
    """Create a new scientific study."""
    try:
        if study.doi:
            study_id = await scientific_study_service.create_with_doi(study)
        else:
            study_id = await scientific_study_service.create(study)
            
        return StatusResponse(
            status="success",
            message="Scientific study created successfully",
            details={"id": study_id}
        )
    except Exception as e:
        logger.error(f"Error creating scientific study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{study_id}", response_model=ScientificStudy)
async def get_scientific_study(study_id: str):
    """Retrieve a scientific study by ID."""
    try:
        study = await scientific_study_service.get_by_id(study_id)
        if not study:
            raise HTTPException(status_code=404, detail="Scientific study not found")
        return study
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving scientific study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{study_id}", response_model=StatusResponse)
async def update_scientific_study(study_id: str, study: ScientificStudy):
    """Update an existing scientific study."""
    try:
        success = await scientific_study_service.update(study_id, study)
        if not success:
            raise HTTPException(status_code=404, detail="Scientific study not found")
            
        return StatusResponse(
            status="success",
            message="Scientific study updated successfully",
            details={"id": study_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating scientific study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{study_id}", response_model=StatusResponse)
async def delete_scientific_study(study_id: str):
    """Delete a scientific study."""
    try:
        success = await scientific_study_service.delete(study_id)
        if not success:
            raise HTTPException(status_code=404, detail="Scientific study not found")
            
        return StatusResponse(
            status="success",
            message="Scientific study deleted successfully",
            details={"id": study_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting scientific study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[SearchResponse])
async def search_scientific_studies(
    query_text: str,
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    min_score: Optional[float] = Query(default=0.5, ge=0.0, le=1.0)
):
    """Search for similar scientific studies."""
    try:
        results = await scientific_study_service.search_similar_studies(
            query_text=query_text,
            limit=limit,
            min_score=min_score
        )
        return results
    except Exception as e:
        logger.error(f"Error searching scientific studies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discipline/{discipline}", response_model=List[ScientificStudy])
async def get_scientific_studies_by_discipline(
    discipline: str,
    limit: Optional[int] = Query(default=10, ge=1, le=100)
):
    """Get scientific studies by discipline."""
    try:
        studies = await scientific_study_service.search_by_discipline(
            discipline=discipline,
            limit=limit
        )
        return studies
    except Exception as e:
        logger.error(f"Error getting scientific studies by discipline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{study_id}/citations", response_model=StatusResponse)
async def update_scientific_study_citations(study_id: str, citations: List[str]):
    """Update citations for a scientific study."""
    try:
        success = await scientific_study_service.update_citations(study_id, citations)
        if not success:
            raise HTTPException(status_code=404, detail="Scientific study not found")
            
        return StatusResponse(
            status="success",
            message="Citations updated successfully",
            details={"id": study_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating citations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
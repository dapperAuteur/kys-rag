from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from app.models.models import SearchQuery, SearchResponse
from app.services.services import search_service
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/search", tags=["Search"])

@router.post("/", response_model=List[SearchResponse])
async def search_all_content(query: SearchQuery):
    """Search across all content types."""
    try:
        results = await search_service.search_all(query)
        return results
    except Exception as e:
        logger.error(f"Error searching content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topic/{topic}", response_model=Dict[str, List[Any]])
async def search_by_topic(
    topic: str,
    content_type: Optional[str] = Query(
        default=None,
        description="Filter by 'scientific_study' or 'article'"
    ),
    limit: int = Query(default=10, ge=1, le=100)
):
    """Search for content by topic."""
    try:
        results = await search_service.search_by_topic(
            topic=topic,
            content_type=content_type,
            limit=limit
        )
        return results
    except Exception as e:
        logger.error(f"Error searching by topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent", response_model=Dict[str, List[Any]])
async def search_recent_content(
    days: int = Query(default=30, ge=1, le=365),
    content_type: Optional[str] = Query(
        default=None,
        description="Filter by 'scientific_study' or 'article'"
    ),
    limit: int = Query(default=10, ge=1, le=100)
):
    """Search for recent content."""
    try:
        results = await search_service.search_recent(
            days=days,
            content_type=content_type,
            limit=limit
        )
        return results
    except Exception as e:
        logger.error(f"Error searching recent content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/related/{content_type}/{content_id}", response_model=Dict[str, List[Any]])
async def find_related_content(
    content_type: str,
    content_id: str,
    limit: int = Query(default=5, ge=1, le=20)
):
    """Find content related to a specific item."""
    try:
        if content_type not in ["scientific_study", "article"]:
            raise HTTPException(status_code=400, detail="Invalid content type")
            
        results = await search_service.find_related_content(
            content_id=content_id,
            content_type=content_type,
            limit=limit
        )
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding related content: {e}")
        raise HTTPException(status_code=500, detail=str(e))
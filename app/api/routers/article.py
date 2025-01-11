from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.models import Article, Claim, ScientificStudy, SearchResponse, StatusResponse, ArticleCreate, ArticleResponse
from app.services.services import article_service
import logging
from app.core.database import database
from datetime import datetime, timezone
from bson.codec_options import CodecOptions
from bson import ObjectId

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/articles", tags=["Articles"])

@router.post("/", response_model=ArticleResponse)
async def create_article(article: ArticleCreate):
    """
    Create a new article in the database.
    
    This endpoint handles:
    - Converting the HttpUrl to a string for MongoDB storage
    - Ensuring all dates are in UTC format
    - Proper error handling and logging
    """
    try:
        logger.info(f"Creating article: {article.title}")
        
        # Get the articles collection with timezone awareness
        collection = await database.get_articles_collection()
        collection = collection.with_options(
            codec_options=CodecOptions(tz_aware=True)
        )
        
        # Convert the article to a dictionary, handling HttpUrl conversion
        article_dict = article.model_dump()

        # Ensure all dates are in UTC
        # article_dict["publication_date"] = article.publication_date
        current_time = datetime.now(timezone.utc)

        article_dict.update({
            "created_at": current_time,
            "updated_at": current_time
        })

        logger.info(f"Prepared article data: {article_dict}")
        
        # Insert into database
        result = await collection.insert_one(article_dict)
        
        # Get the created article
        created_article = await collection.find_one({"_id": result.inserted_id})
        
        if not created_article:
            logger.error("Article not found after creation")
            raise HTTPException(status_code=404, detail="Article not found after creation")
        
        # Convert MongoDB _id to string for the response
        created_article["id"] = str(created_article.pop("_id"))
        
        logger.info(f"Successfully created article with ID: {created_article['id']}")
        return ArticleResponse(**created_article)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Error creating article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{article_id}", response_model=Article)
async def get_article(article_id: str):
    """Retrieve an article by ID."""
    try:
        article = await article_service.get_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{article_id}", response_model=StatusResponse)
async def update_article(article_id: str, article: Article):
    """Update an existing article."""
    try:
        success = await article_service.update(article_id, article)
        if not success:
            raise HTTPException(status_code=404, detail="Article not found")
            
        return StatusResponse(
            status="success",
            message="Article updated successfully",
            details={"id": article_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{article_id}", response_model=StatusResponse)
async def delete_article(article_id: str):
    """Delete an article."""
    try:
        success = await article_service.delete(article_id)
        if not success:
            raise HTTPException(status_code=404, detail="Article not found")
            
        return StatusResponse(
            status="success",
            message="Article deleted successfully",
            details={"id": article_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=List[SearchResponse])
async def search_articles(
    query_text: str,
    limit: Optional[int] = Query(default=10, ge=1, le=100),
    min_score: Optional[float] = Query(default=0.5, ge=0.0, le=1.0)
):
    """Search for similar articles."""
    try:
        results = await article_service.search_similar_articles(
            query_text=query_text,
            limit=limit,
            min_score=min_score
        )
        return results
    except Exception as e:
        logger.error(f"Error searching articles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{article_id}/claims", response_model=StatusResponse)
async def add_claim(article_id: str, claim: Claim):
    """Add a new claim to an article."""
    try:
        success = await article_service.add_claim(article_id, claim)
        if not success:
            raise HTTPException(status_code=404, detail="Article not found")
            
        return StatusResponse(
            status="success",
            message="Claim added successfully",
            details={"article_id": article_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding claim: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{article_id}/scientific-studies", response_model=List[ScientificStudy])
async def get_related_scientific_studies(article_id: str):
    """Get scientific studies related to an article."""
    try:
        studies = await article_service.get_related_scientific_studies(article_id)
        return studies
    except Exception as e:
        logger.error(f"Error getting related scientific studies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get the current status of the articles service"""
    try:
        collection = await database.get_articles_collection()
        count = await collection.count_documents({})
        
        return StatusResponse(
            status="healthy",
            message="Articles service is running",
            details={
                "total_articles": count,
                "last_checked": datetime.now(timezone.utc).isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Error checking service status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve service status"
        )
    
@router.post("/{article_id}/scientific-studies/{study_id}", response_model=StatusResponse)
async def link_scientific_study(article_id: str, study_id: str):
    """Link a scientific study to an article."""
    try:
        success = await article_service.link_scientific_study(article_id, study_id)
        if not success:
            raise HTTPException(status_code=404, detail="Article or scientific study not found")
            
        return StatusResponse(
            status="success",
            message="Scientific study linked successfully",
            details={
                "article_id": article_id,
                "study_id": study_id
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking scientific study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{article_id}/claims/{claim_index}/verify", response_model=StatusResponse)
async def verify_claim(
    article_id: str,
    claim_index: int,
    verification_notes: str,
    confidence_score: float = Query(ge=0.0, le=1.0),
    verified: bool = False
):
    """Update the verification status of a claim."""
    try:
        success = await article_service.verify_claim(
            article_id,
            claim_index,
            verification_notes,
            confidence_score,
            verified
        )
        if not success:
            raise HTTPException(status_code=404, detail="Article or claim not found")
            
        return StatusResponse(
            status="success",
            message="Claim verification updated successfully",
            details={
                "article_id": article_id,
                "claim_index": claim_index
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying claim: {e}")
        raise HTTPException(status_code=500, detail=str(e))
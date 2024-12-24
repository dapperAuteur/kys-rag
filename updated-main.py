from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
import logging
from typing import List
from models import (
    ScientificStudy, Article, SearchQuery, 
    SearchResponse, StatusResponse
)
from services import study_service, article_service
from database import database
from config import get_settings

# Configure logging
logging.basicConfig(level=get_settings().LOG_LEVEL)
logger = logging.getLogger(__name__)

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    try:
        logger.info("Starting application...")
        await database.connect()
        yield
    finally:
        logger.info("Shutting down application...")
        await database.close()

# Create FastAPI application
app = FastAPI(
    title="Science Decoder",
    description="Scientific paper analysis API",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/", response_model=StatusResponse)
async def read_root():
    """Root endpoint"""
    return StatusResponse(
        status="ok",
        message="Welcome to the Science Decoder API!",
        details={"version": "2.0.0"}
    )

# Scientific Study Routes
@app.post("/studies/", response_model=StatusResponse)
async def create_study(study: ScientificStudy):
    """Create a new scientific study"""
    try:
        logger.info(f"Creating new study: {study.title}")
        study_id = await study_service.save_study(study)
        logger.info(f"Study created successfully with ID: {study_id}")
        return StatusResponse(
            status="success",
            message="Study created successfully",
            details={"id": study_id}
        )
    except Exception as e:
        logger.error(f"Error creating study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/studies/{study_id}", response_model=ScientificStudy)
async def get_study(study_id: str):
    """Retrieve a study by ID"""
    try:
        logger.info(f"Retrieving study: {study_id}")
        study = await study_service.get_study_by_id(study_id)
        if not study:
            raise HTTPException(status_code=404, detail="Study not found")
        return study
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Article Routes
@app.post("/articles/", response_model=StatusResponse)
async def create_article(article: Article):
    """Create a new article"""
    try:
        logger.info(f"Creating new article: {article.title}")
        # Verify cited studies exist
        for study_id in article.cited_studies:
            study = await study_service.get_study_by_id(study_id)
            if not study:
                raise HTTPException(
                    status_code=404,
                    detail=f"Cited study not found: {study_id}"
                )
        
        article_id = await article_service.save_article(article)
        logger.info(f"Article created successfully with ID: {article_id}")
        return StatusResponse(
            status="success",
            message="Article created successfully",
            details={"id": article_id}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/articles/{article_id}", response_model=Article)
async def get_article(article_id: str):
    """Retrieve an article by ID"""
    try:
        logger.info(f"Retrieving article: {article_id}")
        article = await article_service.get_article_by_id(article_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Search Routes
@app.post("/search/", response_model=List[SearchResponse])
async def search_content(query: SearchQuery):
    """Search for studies and articles"""
    try:
        logger.info(f"Searching with query: {query.query_text}")
        results = []
        
        if query.content_type in ["study", "all"]:
            study_results = await study_service.search_similar_studies(query)
            results.extend([
                SearchResponse(
                    content_type="study",
                    study=result.study,
                    score=result.score
                ) for result in study_results
            ])
            
        if query.content_type in ["article", "all"]:
            article_results = await article_service.search_similar_articles(query)
            results.extend([
                SearchResponse(
                    content_type="article",
                    article=result.article,
                    score=result.score
                ) for result in article_results
            ])
            
        # Sort combined results by score
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:query.limit]
        
    except Exception as e:
        logger.error(f"Error searching content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
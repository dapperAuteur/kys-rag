from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
import logging
from typing import List
from models import (
    Study, Article, SearchQuery, SearchResponse, StatusResponse, PydanticObjectId
)
from services import study_service, article_service, search_service
from database import database
from config import get_settings

# Configure logging for the application
settings = get_settings()
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage database connections during application lifecycle"""
    try:
        logger.info("Starting application and connecting to database...")
        await database.connect()
        yield
    finally:
        logger.info("Shutting down application...")
        await database.close()

# Create FastAPI application with metadata
app = FastAPI(
    title="Science Decoder",
    description="API for analyzing scientific papers and articles",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/", response_model=StatusResponse)
async def read_root():
    """Root endpoint to check API status"""
    return StatusResponse(
        status="success",
        message="Welcome to the Science Decoder API!",
        details={"version": "2.0.0"}
    )

# Study Routes
@app.post("/studies/", response_model=StatusResponse)
async def create_study(study: Study):
    """Create a new scientific study with vector embeddings"""
    try:
        logger.info(f"Creating new study: {study.title}")
        study_id = await study_service.create_study(study)
        return StatusResponse(
            status="success",
            message="Study created successfully",
            details={"id": str(study_id)}
        )
    except Exception as e:
        logger.error(f"Error creating study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/studies/{study_id}", response_model=Study)
async def get_study(study_id: str):
    """Retrieve a study by its ID"""
    try:
        logger.info(f"Retrieving study: {study_id}")
        study = await study_service.get_study(study_id)
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
    """Create a new article with vector embeddings"""
    try:
        logger.info(f"Creating new article: {article.title}")
        
        # Verify all cited studies exist
        for study_id in article.cited_studies:
            study = await study_service.get_study(str(study_id))
            if not study:
                raise HTTPException(
                    status_code=404,
                    detail=f"Cited study not found: {study_id}"
                )
        
        article_id = await article_service.create_article(article)
        return StatusResponse(
            status="success",
            message="Article created successfully",
            details={"id": str(article_id)}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating article: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/articles/{article_id}", response_model=Article)
async def get_article(article_id: str):
    """Retrieve an article by its ID"""
    try:
        logger.info(f"Retrieving article: {article_id}")
        article = await article_service.get_article(article_id)
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
    """Search for studies and articles using vector similarity"""
    try:
        logger.info(f"Searching with query: {query.query_text}")
        results = await search_service.search(query)
        return results
    except Exception as e:
        logger.error(f"Error searching content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
import logging
from typing import List
from models import Study, SearchQuery, SearchResponse, StatusResponse
from services import study_service
from database import database
from config import get_settings

# Configure logging
logging.basicConfig(level=get_settings().LOG_LEVEL)
logger = logging.getLogger(__name__)

# Application lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown"""
    try:
        # Startup
        logger.info("Starting application...")
        await database.connect()
        yield
    finally:
        # Shutdown
        logger.info("Shutting down application...")
        await database.disconnect()

# Create FastAPI application
app = FastAPI(
    title="Science Decoder",
    description="Scientific paper search and analysis API",
    version="2.0.0",
    lifespan=lifespan
)

@app.get("/", response_model=StatusResponse)
async def read_root():
    """Root endpoint - application status"""
    return StatusResponse(
        status="ok",
        message="Welcome to the Science Decoder API!",
        details={"version": "2.0.0"}
    )

@app.post("/studies/", response_model=StatusResponse)
async def create_study(study: Study):
    """Create a new study"""
    try:
        study_id = await study_service.save_study(study)
        return StatusResponse(
            status="success",
            message="Study created successfully",
            details={"id": study_id}
        )
    except Exception as e:
        logger.error(f"Error creating study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/studies/{study_id}", response_model=Study)
async def get_study(study_id: str):
    """Retrieve a study by ID"""
    try:
        study = await study_service.get_study_by_id(study_id)
        if not study:
            raise HTTPException(status_code=404, detail="Study not found")
        return study
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving study: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/", response_model=List[SearchResponse])
async def search_studies(query: SearchQuery):
    """Search for similar studies"""
    try:
        results = await study_service.search_similar_studies(query)
        return results
    except Exception as e:
        logger.error(f"Error searching studies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
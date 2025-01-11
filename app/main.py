from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import logging
from app.models.models import StatusResponse
from app.core.database import database
from app.core.config import get_settings
from app.api.routers import (
    scientific_study_router,
    article_router,
    search_router,
    chat_router,
    pdf_router
)

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
    description="Scientific content analysis and verification API",
    version="2.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(scientific_study_router)
app.include_router(article_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(pdf_router)

@app.get("/", response_model=StatusResponse)
async def read_root():
    """Root endpoint - application status and health check"""
    try:
        # Perform database health check
        db_healthy = await database.health_check()
        
        if not db_healthy:
            raise HTTPException(
                status_code=503,
                detail="Database health check failed"
            )
        
        return StatusResponse(
            status="ok",
            message="Welcome to the Science Decoder API!",
            details={
                "version": "2.0.0",
                "database_status": "healthy"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
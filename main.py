from fastapi import FastAPI, HTTPException, Body
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModel, AutoModelForQuestionAnswering
from pydantic import BaseModel, Field
import torch
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import logging
from typing import List, Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Configure detailed logging format for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration class to centralize all settings
class Config:
    """Central configuration class for application settings"""
    MONGODB_ATLAS_URI = os.getenv("MONGODB_ATLAS_URI", "mongodb://localhost:27017/")
    MODEL_NAME = "allenai/scibert_scivocab_uncased"
    EMBEDDING_DIM = 768
    MAX_SEQUENCE_LENGTH = 512
    DATABASE_NAME = "science_decoder"
    COLLECTION_NAME = "studies"

# Data Models with enhanced type safety
class Study(BaseModel):
    """Model representing a scientific study input"""
    title: str
    text: str
    topic: str
    discipline: str
    vector: Optional[List[float]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

class StudyDocument(Study):
    """Extended study model for database storage"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class QuestionRequest(BaseModel):
    """Model for question-answering requests"""
    question: str
    context: str

class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass

# Database Management with async operations
class DatabaseManager:
    def __init__(self, uri: str):
        """Initialize database connection with provided URI"""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[Any] = None
        self.studies_collection: Optional[Any] = None
        self.uri = uri

    async def connect(self) -> None:
        """Establish async connection to MongoDB"""
        try:
            logger.info("Establishing MongoDB connection...")
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client[Config.DATABASE_NAME]
            self.studies_collection = self.db[Config.COLLECTION_NAME]
            
            # Verify connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise DatabaseError(f"Failed to connect to MongoDB: {str(e)}")

    async def disconnect(self) -> None:
        """Close database connection"""
        if self.client:
            logger.info("Closing MongoDB connection...")
            self.client.close()
            logger.info("MongoDB connection closed")

    async def save_study(self, study: StudyDocument) -> str:
        """Save a study document to MongoDB"""
        try:
            logger.info(f"Saving study: {study.title}")
            result = await self.studies_collection.insert_one(study.dict())
            logger.info(f"Successfully saved study with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            error_msg = f"Failed to save study {study.title}: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)

    async def get_all_vectors(self) -> List[np.ndarray]:
        """Retrieve all vectors from the database"""
        try:
            logger.info("Retrieving vectors from database")
            vectors = []
            async for study in self.studies_collection.find(
                {"vector": {"$exists": True}},
                projection={"vector": 1}
            ):
                if study.get("vector"):
                    vector = np.array(study["vector"], dtype="float32").reshape(1, -1)
                    vectors.append(vector)
            
            logger.info(f"Retrieved {len(vectors)} vectors")
            return vectors
        except Exception as e:
            error_msg = f"Failed to retrieve vectors: {str(e)}"
            logger.error(error_msg)
            raise DatabaseError(error_msg)

# FAISS Index Management
class FAISSManager:
    def __init__(self):
        """Initialize FAISS index for vector similarity search"""
        self.index = faiss.IndexFlatL2(Config.EMBEDDING_DIM)
        logger.info("FAISS index initialized")

    async def load_vectors_from_db(self, db_manager: DatabaseManager) -> None:
        """Load existing vectors from MongoDB into FAISS index"""
        try:
            logger.info("Loading vectors into FAISS index...")
            vectors = await db_manager.get_all_vectors()
            
            if vectors:
                vectors_array = np.vstack(vectors)
                self.index.add(vectors_array)
                logger.info(f"Added {len(vectors)} vectors to FAISS index")
            else:
                logger.info("No vectors found in database")
        except Exception as e:
            logger.error(f"Failed to load vectors into FAISS: {str(e)}")
            raise

    def search(self, query_vector: np.ndarray, k: int = 5) -> tuple:
        """Search for similar vectors in the index"""
        try:
            logger.debug(f"Searching for {k} similar vectors")
            return self.index.search(query_vector.astype("float32"), k)
        except Exception as e:
            logger.error(f"FAISS search failed: {str(e)}")
            raise

# Model Management with async support
class ModelManager:
    def __init__(self):
        """Initialize ML models and components"""
        self.tokenizer = None
        self.embedding_model = None
        self.qa_model = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.initialize_models()

    def initialize_models(self) -> None:
        """Initialize all required ML models"""
        try:
            logger.info("Initializing ML models...")
            self.tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_NAME)
            self.embedding_model = AutoModel.from_pretrained(Config.MODEL_NAME)
            self.qa_model = AutoModelForQuestionAnswering.from_pretrained(Config.MODEL_NAME)
            
            # Set models to evaluation mode
            self.embedding_model.eval()
            self.qa_model.eval()
            logger.info("ML models initialized successfully")
        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text asynchronously"""
        def _generate() -> List[float]:
            try:
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=Config.MAX_SEQUENCE_LENGTH
                )
                
                with torch.no_grad():
                    outputs = self.embedding_model(**inputs)
                    vector = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
                    return vector if isinstance(vector, list) else [vector]
            except Exception as e:
                logger.error(f"Embedding generation failed: {str(e)}")
                raise

        return await asyncio.get_event_loop().run_in_executor(
            self.executor,
            _generate
        )

# Initialize FastAPI application
app = FastAPI(
    title="Science Decoder API",
    description="API for scientific text analysis and question answering",
    version="1.0.0"
)

# Initialize components
db_manager = DatabaseManager(Config.MONGODB_ATLAS_URI)
model_manager = ModelManager()
faiss_manager = FAISSManager()

# API Endpoints
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Check the health status of all system components"""
    try:
        # Verify database connection
        await db_manager.studies_collection.find_one()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"

    return {
        "status": "healthy",
        "components": {
            "database": db_status,
            "models": "healthy" if model_manager.tokenizer else "unhealthy",
            "faiss": "healthy" if faiss_manager.index.ntotal >= 0 else "unhealthy"
        }
    }

@app.post("/save-study")
async def save_study(study: Study) -> Dict[str, Any]:
    """Save a new study with its embedding vector"""
    try:
        logger.info(f"Processing save-study request for: {study.title}")
        
        # Generate embedding
        vector = await model_manager.generate_embedding(study.text)
        
        # Create study document
        study_doc = StudyDocument(
            **study.dict(),
            vector=vector,
            created_at=datetime.utcnow()
        )
        
        # Save to MongoDB
        study_id = await db_manager.save_study(study_doc)
        
        # Update FAISS index
        vector_array = np.array([vector], dtype="float32")
        faiss_manager.index.add(vector_array)
        
        logger.info(f"Study saved successfully with ID: {study_id}")
        return {
            "status": "success",
            "message": "Study saved successfully",
            "id": study_id
        }
    except Exception as e:
        error_msg = f"Failed to save study: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/search-studies")
async def search_studies(query: Dict[str, str] = Body(...)) -> Dict[str, Any]:
    """Search for similar studies using semantic search"""
    try:
        query_text = query.get("query_text")
        if not query_text:
            raise HTTPException(status_code=400, detail="query_text field is required")
        
        # Generate embedding for query
        query_vector = await model_manager.generate_embedding(query_text)
        query_vector = np.array([query_vector], dtype="float32")
        
        # Search FAISS index
        distances, indices = faiss_manager.search(query_vector)
        
        # Fetch matching studies
        results = []
        for idx in indices[0]:
            study = await db_manager.studies_collection.find_one({}, skip=int(idx))
            if study:
                study["_id"] = str(study["_id"])
                study.pop('vector', None)  # Remove vector from response
                results.append(study)
        
        return {"results": results}
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.post("/ask")
async def answer_question(request: QuestionRequest) -> Dict[str, str]:
    """Answer a question based on provided context"""
    try:
        def _generate_answer() -> str:
            inputs = model_manager.tokenizer(
                request.question,
                request.context,
                return_tensors="pt",
                truncation=True,
                max_length=Config.MAX_SEQUENCE_LENGTH
            )
            
            with torch.no_grad():
                outputs = model_manager.qa_model(**inputs)
                start_scores = outputs.start_logits
                end_scores = outputs.end_logits
                
                start_idx = torch.argmax(start_scores)
                end_idx = torch.argmax(end_scores)
                
                if end_idx < start_idx:
                    end_idx = start_idx + 1
                
                tokens = model_manager.tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
                answer = model_manager.tokenizer.convert_tokens_to_string(
                    tokens[start_idx:end_idx + 1]
                )
                
                return answer.strip()

        answer = await asyncio.get_event_loop().run_in_executor(
            model_manager.executor,
            _generate_answer
        )
        
        if not answer:
            return {"answer": "Could not find answer in context"}
        
        return {"answer": answer}
    except Exception as e:
        error_msg = f"Question answering failed: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/")
def read_root() -> Dict[str, str]:
    """Root endpoint returning welcome message"""
    return {"message": "Welcome to the Science Decoder Tool!"}

# Application lifecycle events
@app.on_event("startup")
async def startup_event() -> None:
    """Initialize system components on startup"""
    try:
        logger.info("Starting application initialization...")
        await db_manager.connect()
        await faiss_manager.load_vectors_from_db(db_manager)
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Clean up system resources on shutdown"""
    try:
        logger.info("Starting application shutdown...")
        await db_manager.disconnect()
        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Application shutdown error: {str(e)}")
        raise
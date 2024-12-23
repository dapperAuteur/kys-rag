from fastapi import FastAPI, HTTPException, Body
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModel, AutoModelForQuestionAnswering
from pydantic import BaseModel, Field
import torch
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv
import logging
from typing import List, Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration Settings
class Config:
    MONGODB_ATLAS_URI = os.getenv("MONGODB_ATLAS_URI", "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/")
    MONGODB_LOCAL_URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017/")
    MODEL_NAME = "allenai/scibert_scivocab_uncased"
    EMBEDDING_DIM = 768
    MAX_SEQUENCE_LENGTH = 512

# Data Models
class Study(BaseModel):
    """Model representing a scientific study."""
    title: str
    text: str
    topic: str
    discipline: str
    vector: Optional[List[float]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

class QuestionRequest(BaseModel):
    """Model for question-answering requests."""
    question: str
    context: str

# Database Management
class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.studies_collection = None
        self._initialize_connection()

    def _initialize_connection(self):
        """Initialize MongoDB connection with fallback to local instance."""
        try:
            # Try Atlas connection first
            self.client = MongoClient(Config.MONGODB_ATLAS_URI, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            logger.info("Connected to MongoDB Atlas")
        except ConnectionFailure:
            try:
                # Fall back to local MongoDB
                self.client = MongoClient(Config.MONGODB_LOCAL_URI, serverSelectionTimeoutMS=5000)
                self.client.admin.command('ping')
                logger.info("Connected to local MongoDB")
            except ConnectionFailure as e:
                logger.error("Failed to connect to MongoDB")
                raise ConnectionFailure("Could not connect to MongoDB (neither Atlas nor local)")

        self.db = self.client["science_decoder"]
        self.studies_collection = self.db["studies"]

    def get_all_vectors(self):
        """Retrieve all vectors from the database synchronously."""
        vectors = []
        try:
            # Use regular for loop since we're using synchronous PyMongo
            for study in self.studies_collection.find():
                if "vector" in study and len(study["vector"]) == Config.EMBEDDING_DIM:
                    vector = np.array(study["vector"], dtype="float32").reshape(1, -1)
                    vectors.append(vector)
            return vectors
        except Exception as e:
            logger.error(f"Error retrieving vectors: {str(e)}")
            raise
# FAISS Index Management
class FAISSManager:
    def __init__(self):
        self.index = faiss.IndexFlatL2(Config.EMBEDDING_DIM)
    def load_vectors_from_db(self, db_manager: DatabaseManager):
        """Load existing vectors from MongoDB into FAISS index."""
        logger.info("Loading vectors from MongoDB into FAISS index...")
        try:
            vectors = db_manager.get_all_vectors()
            if vectors:
                vectors_array = np.vstack(vectors)
                self.index.add(vectors_array)
                logger.info(f"Added {len(vectors)} vectors to FAISS index")
            else:
                logger.info("No vectors found in database")
        except Exception as e:
            logger.error(f"Error loading vectors: {str(e)}")
            raise
    def search(self, query_vector: np.ndarray, k: int = 5) -> tuple:
        """Search for similar vectors in the index."""
        return self.index.search(query_vector.astype("float32"), k)

# Model Management
class ModelManager:
    def __init__(self):
        self.tokenizer = None
        self.embedding_model = None
        self.qa_model = None
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.initialize_models()

    def initialize_models(self):
        """Initialize all required models."""
        logger.info("Initializing models...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(Config.MODEL_NAME)
            self.embedding_model = AutoModel.from_pretrained(Config.MODEL_NAME)
            self.qa_model = AutoModelForQuestionAnswering.from_pretrained(Config.MODEL_NAME)
            
            # Put models in evaluation mode
            self.embedding_model.eval()
            self.qa_model.eval()
            logger.info("Models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text asynchronously."""
        def _generate():
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

        return await asyncio.get_event_loop().run_in_executor(self.executor, _generate)

# FAISS Index Management
class FAISSManager:
    def __init__(self):
        self.index = faiss.IndexFlatL2(Config.EMBEDDING_DIM)

    async def load_vectors_from_db(self, db_manager: DatabaseManager):
        """Load existing vectors from MongoDB into FAISS index."""
        logger.info("Loading vectors from MongoDB into FAISS index...")
        vectors_to_add = []
        
        async for study in db_manager.studies_collection.find():
            if "vector" in study and len(study["vector"]) == Config.EMBEDDING_DIM:
                vector = np.array(study["vector"], dtype="float32").reshape(1, -1)
                vectors_to_add.append(vector)
        
        if vectors_to_add:
            vectors_array = np.vstack(vectors_to_add)
            self.index.add(vectors_array)
            logger.info(f"Added {len(vectors_to_add)} vectors to FAISS index")

    def search(self, query_vector: np.ndarray, k: int = 5) -> tuple:
        """Search for similar vectors in the index."""
        return self.index.search(query_vector.astype("float32"), k)

# Initialize application components
db_manager = DatabaseManager()
model_manager = ModelManager()
faiss_manager = FAISSManager()

# Initialize FastAPI application
app = FastAPI(title="Science Decoder API")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check the health status of all system components."""
    try:
        # Check MongoDB connection
        db_status = "healthy" if db_manager.studies_collection else "unhealthy"
        
        # Check model status
        model_status = "healthy" if (
            model_manager.tokenizer and 
            model_manager.embedding_model and 
            model_manager.qa_model
        ) else "unhealthy"
        
        # Check FAISS index
        faiss_status = "healthy" if faiss_manager.index.ntotal >= 0 else "unhealthy"
        
        return {
            "status": "healthy",
            "components": {
                "database": db_status,
                "models": model_status,
                "faiss": faiss_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="System health check failed")

@app.post("/save-study")
async def save_study(study: Study):
    """Save a new study with its embedding vector."""
    try:
        # Generate embedding
        vector = await model_manager.generate_embedding(study.text)
        study.vector = vector
        
        # Save to MongoDB
        result = await db_manager.studies_collection.insert_one(study.dict())
        
        # Update FAISS index
        vector_array = np.array([vector], dtype="float32")
        faiss_manager.index.add(vector_array)
        
        return {
            "status": "success",
            "message": "Study saved successfully",
            "id": str(result.inserted_id)
        }
    except Exception as e:
        logger.error(f"Error saving study: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-studies")
async def search_studies(query: Dict[str, str] = Body(...)):
    """Search for similar studies using semantic search."""
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
                study.pop('vector', None)
                results.append(study)
        
        return {"results": results}
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def answer_question(request: QuestionRequest):
    """Answer a question based on provided context."""
    try:
        def _generate_answer():
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
                
                # Ensure valid answer span
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
        logger.error(f"Question answering failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Startup event to load existing vectors
@app.on_event("startup")
async def startup_event():
    """Initialize system components on startup."""
    try:
        # Note: This is now synchronous but runs in startup
        faiss_manager.load_vectors_from_db(db_manager)
        logger.info("Startup completed successfully")
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}")
        raise
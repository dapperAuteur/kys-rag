import logging
from datetime import datetime
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
import torch
from transformers import AutoTokenizer, AutoModel

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# MongoDB connection using Motor
client = AsyncIOMotorClient("mongodb://localhost:27017/")
db = client["science_decoder"]
studies_collection = db["studies"]

# Hugging Face model setup
logger.info("Initializing models...")

# Use CPU explicitly
device = torch.device("cpu")
logger.info(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
model.to(device)  # Move the model to CPU
model.eval()
logger.info("Model loaded successfully.")

# Pydantic models
class Study(BaseModel):
    title: str
    text: str
    topic: str
    discipline: str

class EmbeddingTestRequest(BaseModel):
    text: str

@app.on_event("startup")
async def startup_event():
    """Test MongoDB connection on startup."""
    try:
        await studies_collection.database.command("ping")
        logger.info("Connected to MongoDB successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


@app.get("/")
def read_root():
    """Welcome route."""
    return {"message": "Welcome to the Science Decoder Tool!"}


@app.post("/save-study")
async def save_study(study: Study) -> Dict[str, Any]:
    """Save a new study to MongoDB."""
    try:
        logger.info(f"Processing save-study request for: {study.title}")
        
        # Generate embedding
        embedding = await generate_embedding(study.text)
        logger.info(f"Embedding generated successfully: {len(embedding)} dimensions")
        
        # Add study to MongoDB
        study_doc = {
            "title": study.title,
            "text": study.text,
            "topic": study.topic,
            "discipline": study.discipline,
            "vector": embedding,
            "created_at": datetime.utcnow()
        }
        result = await studies_collection.insert_one(study_doc)
        logger.info(f"Study saved successfully with ID: {result.inserted_id}")
        
        return {
            "status": "success",
            "message": "Study saved successfully",
            "id": str(result.inserted_id)
        }
    except Exception as e:
        logger.error(f"Error saving study: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error saving study: {str(e)}")


@app.get("/get-studies/{topic}")
async def get_studies_by_topic(topic: str):
    """Retrieve studies by topic."""
    try:
        cursor = studies_collection.find({"topic": topic})
        studies = []
        async for study in cursor:
            study["_id"] = str(study["_id"])  # Convert ObjectId to string
            studies.append(study)
        return {"studies": studies}
    except Exception as e:
        logger.error(f"Error retrieving studies: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving studies.")


@app.get("/search-studies")
async def search_studies(topic: str = None, discipline: str = None):
    """Search studies by topic and/or discipline."""
    try:
        query = {}
        if topic:
            query["topic"] = topic
        if discipline:
            query["discipline"] = discipline
        
        cursor = studies_collection.find(query)
        studies = []
        async for study in cursor:
            study["_id"] = str(study["_id"])  # Convert ObjectId to string
            studies.append(study)
        return {"studies": studies}
    except Exception as e:
        logger.error(f"Error searching studies: {str(e)}")
        raise HTTPException(status_code=500, detail="Error searching studies.")


@app.post("/test-embedding")
async def test_embedding(request: EmbeddingTestRequest) -> Dict[str, Any]:
    """Test embedding generation in isolation."""
    try:
        text = request.text
        if not text:
            raise HTTPException(status_code=400, detail="The 'text' field is required.")
        
        logger.info(f"Testing embedding generation for text: {text}")
        
        # Generate embedding
        embedding = await generate_embedding(text)
        logger.debug(f"Generated embedding: {embedding[:10]}... (truncated for brevity)")
        
        return {
            "status": "success",
            "embedding_preview": embedding[:10],  # First 10 values for brevity
            "dimensions": len(embedding)
        }
    except Exception as e:
        error_msg = f"Error generating embedding: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


async def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a given text."""
    if not text:
        raise ValueError("Empty text provided for embedding generation.")
    
    def _generate() -> List[float]:
        try:
            logger.debug(f"Tokenizing text of length {len(text)}...")
            inputs = tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(device)  # Ensure input tensors are on the same device as the model
            
            logger.debug(f"Tokenized inputs: {inputs}")
            logger.debug("Generating embedding...")
            
            with torch.no_grad():
                outputs = model(**inputs)
                vector = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
            
            logger.debug(f"Generated embedding: {vector[:10]}... (truncated for brevity)")
            return vector
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}", exc_info=True)
            raise
    
    return await asyncio.get_event_loop().run_in_executor(None, _generate)

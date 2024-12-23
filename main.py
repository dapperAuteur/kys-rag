from fastapi import FastAPI, HTTPException, Body
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModel, AutoModelForQuestionAnswering
from pydantic import BaseModel
import torch
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_ATLAS_URI = os.getenv("MONGODB_ATLAS_URI", "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/")
MONGODB_LOCAL_URI = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017/")

def connect_to_mongodb():
    """Try to connect to MongoDB Atlas first, then fall back to local if needed"""
    try:
        # Try Atlas connection first
        client = MongoClient(MONGODB_ATLAS_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        logger.info("Connected to MongoDB Atlas")
        return client
    except ConnectionFailure:
        try:
            # Fall back to local MongoDB
            client = MongoClient(MONGODB_LOCAL_URI, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            logger.info("Connected to local MongoDB, (neither Atlas nor local)")
            return client
        except ConnectionFailure:
            logger.error("Failed to connect to MongoDB")
            raise ConnectionFailure("Could not connect to MongoDB (neither Atlas nor local)")

# Initialize MongoDB client
try:
    mongo_client = connect_to_mongodb()
    db = mongo_client["science_decoder"]
    studies_collection = db["studies"]
except ConnectionFailure as e:
    logger.warning(f"Warning: {str(e)}")
    studies_collection = None

class QuestionRequest(BaseModel):
    question: str
    context: str

class Study(BaseModel):
    title: str
    text: str
    topic: str
    discipline: str
    vector: list = []  # Optional vector embedding

    class Config:
        arbitrary_types_allowed = True

print(f"MongoDB documents: {studies_collection.count_documents({})}")

# Initialize tokenizer and models
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
embedding_model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
qa_model = AutoModelForQuestionAnswering.from_pretrained("allenai/scibert_scivocab_uncased")

# Initialize FAISS index
index = faiss.IndexFlatL2(768)  # 768 is the dimension of SciBERT embeddings

logger.info(f"BEFORE FAISS index now contains {index.ntotal} vectors")

# Load existing embeddings from MongoDB with validation
logger.info("Loading vectors from MongoDB into FAISS index...")
existing_studies = studies_collection.find()
vectors_to_add = []

for study in existing_studies:
    logger.info(f"Processing document: {study.get('title', 'No title')} with ID: {study.get('_id')}")
    
    if "vector" in study:
        vector = study["vector"]
        logger.info(f"Vector type: {type(vector)}, Length/Shape: {len(vector) if isinstance(vector, list) else vector.shape}")
        
        # Validate vector
        if isinstance(vector, list) and len(vector) == 768:
            try:
                vector = np.array(vector, dtype="float32").reshape(1, -1)
                vectors_to_add.append(vector)
            except Exception as e:
                logger.error(f"Error converting vector for document {study.get('_id')}: {str(e)}")
        else:
            logger.warning(f"Invalid vector dimensions for document {study.get('_id')}. Expected 768, got {len(vector) if isinstance(vector, list) else 'unknown'}")

if vectors_to_add:
    try:
        vectors_to_add = np.vstack(vectors_to_add)
        index.add(vectors_to_add)
        logger.info(f"Successfully added {len(vectors_to_add)} vectors to FAISS index")
    except Exception as e:
        logger.error(f"Error adding vectors to FAISS index: {str(e)}")
else:
    logger.warning("No valid vectors found to add to FAISS index")

logger.info(f"AFTER FAISS index now contains {index.ntotal} vectors")

app = FastAPI()

# Add a diagnostic endpoint to check vector dimensions
@app.get("/check-vectors")
async def check_vectors():
    results = []
    for study in studies_collection.find():
        vector_info = {
            "id": str(study.get("_id")),
            "title": study.get("title", "No title"),
            "has_vector": "vector" in study,
            "vector_length": len(study["vector"]) if "vector" in study else None,
            "vector_type": str(type(study["vector"])) if "vector" in study else None
        }
        results.append(vector_info)
    return {"vectors": results}

@app.post("/repair-vectors")
async def repair_vectors():
    try:
        # Get all documents
        docs = studies_collection.find()
        results = {
            "processed": 0,
            "updated": 0,
            "errors": 0,
            "details": []
        }
        
        for doc in docs:
            results["processed"] += 1
            doc_info = {
                "id": str(doc["_id"]),
                "title": doc.get("title", "No title"),
                "status": "processing"
            }
            
            try:
                # Check if document needs repair (no vector or zero-length vector)
                needs_repair = (
                    "vector" not in doc or 
                    not doc["vector"] or 
                    (isinstance(doc["vector"], list) and len(doc["vector"]) != 768)
                )
                
                if needs_repair:
                    logger.info(f"Repairing vector for document: {doc.get('title', 'No title')}")
                    
                    # Generate new embedding
                    text = doc.get("text", "")
                    if not text:
                        raise ValueError("Document has no text content")
                        
                    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                    with torch.no_grad():
                        output = embedding_model(**inputs)
                        vector = output.last_hidden_state.mean(dim=1).squeeze().numpy()
                        if len(vector.shape) == 0:  # Handle scalar case
                            vector = vector.reshape(1)
                        vector = vector.tolist()
                    
                    # Validate new vector
                    if len(vector) != 768:
                        raise ValueError(f"Generated vector has incorrect dimension: {len(vector)}")
                    
                    # Update document
                    studies_collection.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {"vector": vector}}
                    )
                    
                    results["updated"] += 1
                    doc_info["status"] = "updated"
                    doc_info["vector_length"] = len(vector)
                else:
                    doc_info["status"] = "skipped"
                    doc_info["reason"] = "vector already valid"
                
            except Exception as e:
                results["errors"] += 1
                doc_info["status"] = "error"
                doc_info["error"] = str(e)
                logger.error(f"Error processing document {doc.get('_id')}: {str(e)}")
            
            results["details"].append(doc_info)
        
        # Reinitialize FAISS index
        if results["updated"] > 0:
            global index
            index = faiss.IndexFlatL2(768)
            
            # Reload all vectors
            all_docs = studies_collection.find({"vector": {"$exists": True}})
            vectors = []
            for doc in all_docs:
                if doc.get("vector") and len(doc["vector"]) == 768:
                    vector = np.array(doc["vector"], dtype="float32").reshape(1, -1)
                    vectors.append(vector)
            
            if vectors:
                vectors = np.vstack(vectors)
                index.add(vectors)
                logger.info(f"Reinitialized FAISS index with {len(vectors)} vectors")
        
        results["faiss_index_size"] = index.ntotal
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/check-documents")
async def check_documents():
    docs = list(studies_collection.find())
    return {
        "total_documents": len(docs),
        "documents_with_vectors": sum(1 for doc in docs if "vector" in doc),
        "vector_dimensions": [len(doc["vector"]) if "vector" in doc else None for doc in docs]
    }

@app.post("/save-study")
async def save_study(study: Study):
    try:
        logger.info(f"Starting save operation for study: {study.title}")
        
        if studies_collection is None:
            logger.error("Database connection not available")
            raise HTTPException(status_code=503, detail="Database connection not available")
        
        # Step 1: Tokenize text
        logger.info("Tokenizing text...")
        try:
            inputs = tokenizer(
                study.text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            logger.info("Text tokenized successfully")
        except Exception as e:
            logger.error(f"Tokenization failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Tokenization failed: {str(e)}")
        
        # Step 2: Generate embedding
        logger.info("Generating embedding...")
        try:
            with torch.no_grad():
                outputs = embedding_model(**inputs)
                hidden_states = outputs.last_hidden_state
                logger.info(f"Hidden states shape: {hidden_states.shape}")
                
                # Mean pooling
                attention_mask = inputs['attention_mask']
                mask = attention_mask.unsqueeze(-1).expand(hidden_states.size()).float()
                masked_hidden = hidden_states * mask
                summed = torch.sum(masked_hidden, dim=1)
                count = torch.clamp(mask.sum(1), min=1e-9)
                vector = (summed / count).squeeze().numpy()
                
                if len(vector.shape) == 0:
                    vector = vector.reshape(1)
                vector = vector.tolist()
                
                logger.info(f"Embedding generated successfully, shape: {len(vector)}")
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")
        
        # Step 3: Prepare and validate document
        logger.info("Preparing document...")
        try:
            study_dict = study.dict()
            study_dict["vector"] = vector
            logger.info("Document prepared successfully")
        except Exception as e:
            logger.error(f"Document preparation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Document preparation failed: {str(e)}")
        
        # Step 4: Save to MongoDB
        logger.info("Saving to MongoDB...")
        try:
            result = studies_collection.insert_one(study_dict)
            logger.info(f"Saved to MongoDB with ID: {result.inserted_id}")
        except Exception as e:
            logger.error(f"MongoDB save failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"MongoDB save failed: {str(e)}")
        
        # Step 5: Update FAISS index
        logger.info("Updating FAISS index...")
        try:
            vector_array = np.array([vector], dtype="float32")
            index.add(vector_array)
            logger.info(f"FAISS index updated, now contains {index.ntotal} vectors")
        except Exception as e:
            logger.error(f"FAISS update failed: {str(e)}")
            # Don't raise here - we've already saved to MongoDB
            logger.warning("Document saved to MongoDB but FAISS index update failed")
        
        return {
            "message": "Study saved successfully",
            "id": str(result.inserted_id),
            "vector_length": len(vector),
            "faiss_index_size": index.ntotal
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in save_study: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/get-studies/{topic}")
async def get_studies_by_topic(topic: str):
    if studies_collection is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    try:
        studies = list(studies_collection.find({"topic": topic}))
        # Convert ObjectId to string for JSON serialization
        for study in studies:
            study["_id"] = str(study["_id"])
        return {"studies": studies}
    except Exception as e:
        logger.error(f"Error getting studies by topic: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
def search_vectors(query_vector: list):
   query = np.array([query_vector]).astype("float32")
   distances, indices = index.search(query, k=5)
   return {"distances": distances.tolist(), "indices": indices.tolist()}

@app.post("/ask")
def answer_question(request: QuestionRequest):
  inputs = tokenizer(request.question, request.context, return_tensors="pt", truncation=True, max_length=512)
  outputs = qa_model(**inputs)

  start_scores = outputs.start_logits
  end_scores = outputs.end_logits

  start_index = torch.argmax(start_scores)
  end_index = torch.argmax(end_scores)

  if end_index < start_index:
      end_index = start_index + 1

  all_tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
  answer = tokenizer.convert_tokens_to_string(all_tokens[start_index:end_index + 1])

  answer = answer.strip()

  if not answer:
      return {"answer": "Could not find answer in context", "debug_info": {
          "start_index": start_index.item(),
          "end_index": end_index.item(),
          "total_tokens": len(all_tokens)
      }}
  
  return {"answer": answer}

@app.get("/test-search")
def test_search():
   query_vector = np.random.random(768).astype("float32")
   distances, indices = index.search(np.array([query_vector]), k=3)
   return {"query": query_vector.tolist(), "distances": distances.tolist(), "indices": indices.tolist()}

@app.post("/search-studies")
def search_studies(query: dict = Body(...)):
    logger.info(f"Received search-studies request with body: {query}")
    try:
        query_text = query.get("query_text")
        logger.info(f"Query text: {query_text}")

        if not query_text:
            logger.error("query_text field is missing")
            raise HTTPException(status_code=400, detail="query_text field is required")
        
        # Generate embedding for the query
        try:
            inputs = tokenizer(query_text, return_tensors="pt", truncation=True, max_length=512)
            logger.info(f"Tokenized input: {inputs}")

            with torch.no_grad():
                outputs = embedding_model(**inputs)
                logger.info("Model output generated successfully")
                query_embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
                logger.info(f"Raw embedding shape: {query_embedding.shape}")
                
                # Ensure the embedding is 2D for FAISS
                if len(query_embedding.shape) == 1:
                    query_embedding = query_embedding.unsqueeze(0)
                query_embedding = query_embedding.numpy()
                logger.info(f"Final embedding shape: {query_embedding.shape}")

        except Exception as e:
            logger.error(f"Error during embedding generation: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")
        
        # Search FAISS for similar embeddings
        try:
            logger.info("Starting FAISS search")
            if index.ntotal == 0:
                logger.warning("FAISS index is empty")
                return {"results": [], "warning": "No documents in the index"}
            
            distances, indices = index.search(query_embedding.astype("float32"), k=min(5, index.ntotal))
            logger.info(f"FAISS search complete - Distances: {distances}, Indices: {indices}")
        
        except Exception as e:
            logger.error(f"Error during FAISS search: {str(e)}")
            raise HTTPException(status_code=500, detail=f"FAISS search failed: {str(e)}")
        
        # Fetch studies from MongoDB
        try:
            if studies_collection is None:
                logger.error("MongoDB collection is not initialized")
                raise HTTPException(status_code=503, detail="Database connection not available")
            
            results = []
            total_documents = studies_collection.count_documents({})
            logger.info(f"Total documents in MongoDB: {total_documents}")
            
            for idx in indices[0]:
                if idx < total_documents:
                    study = studies_collection.find_one({}, skip=idx)
                    if study:
                        study["_id"] = str(study["_id"])
                        study.pop('vector', None)  # Remove vector field if present
                        results.append(study)
            
            logger.info(f"Found {len(results)} matching studies")
            return {"results": results}
            
        except Exception as e:
            logger.error(f"Error during MongoDB retrieval: {str(e)}")
            raise HTTPException(status_code=500, detail=f"MongoDB retrieval failed: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error in search_studies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system-status")
async def system_status():
    try:
        # Check MongoDB connection
        mongo_status = "connected" if studies_collection is not None else "disconnected"
        doc_count = studies_collection.count_documents({}) if studies_collection is not None else 0
        
        # Check FAISS index
        faiss_size = index.ntotal if index is not None else 0
        
        # Get sample of documents
        recent_docs = []
        if studies_collection is not None:
            for doc in studies_collection.find().limit(5):
                doc_info = {
                    "id": str(doc["_id"]),
                    "title": doc.get("title", "No title"),
                    "has_vector": "vector" in doc,
                    "vector_length": len(doc["vector"]) if "vector" in doc else None
                }
                recent_docs.append(doc_info)
        
        return {
            "mongodb_status": mongo_status,
            "document_count": doc_count,
            "faiss_index_size": faiss_size,
            "recent_documents": recent_docs
        }
    except Exception as e:
        logger.error(f"Error checking system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/test-embedding")
async def test_embedding():
    try:
        # Test with a simple string
        test_text = "This is a test sentence."
        logger.info("Starting test embedding generation")
        
        # Try tokenization
        inputs = tokenizer(
            test_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        logger.info("Tokenization successful")
        
        # Try embedding
        with torch.no_grad():
            outputs = embedding_model(**inputs)
            vector = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            if len(vector.shape) == 0:
                vector = vector.reshape(1)
            vector = vector.tolist()
        
        return {
            "success": True,
            "vector_length": len(vector),
            "sample_values": vector[:5]  # Return first 5 values of vector
        }
    except Exception as e:
        logger.error(f"Test embedding failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
        
@app.get("/")
def read_root():
  return {"message": "Welcome to the KYS RAG: Science Decoder Tool!"}
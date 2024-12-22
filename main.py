from fastapi import FastAPI, HTTPException
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from pydantic import BaseModel
import torch
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

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
        print("Connected to MongoDB Atlas")
        return client
    except ConnectionFailure:
        try:
            # Fall back to local MongoDB
            client = MongoClient(MONGODB_LOCAL_URI, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            print("Connected to local MongoDB")
            return client
        except ConnectionFailure:
            raise ConnectionFailure("Could not connect to MongoDB (neither Atlas nor local)")

# Initialize MongoDB client
try:
    mongo_client = connect_to_mongodb()
    db = mongo_client["science_decoder"]
    studies_collection = db["studies"]
except ConnectionFailure as e:
    print(f"Warning: {str(e)}")
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

# Initialize existing components
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModelForQuestionAnswering.from_pretrained("allenai/scibert_scivocab_uncased")

# Initialize FAISS index
index = faiss.IndexFlatL2(768)

# Example: Add random data to the index
data = np.random.random((10, 768)).astype("float32")
index.add(data)

app = FastAPI()

@app.post("/save-study")
async def save_study(study: Study):
    if studies_collection is None:
        raise HTTPException(status_code=503, detail="Database connection not available")
    
    try:
        # Convert the study to a dictionary
        study_dict = study.dict()
        
        # Insert into MongoDB
        result = studies_collection.insert_one(study_dict)
        
        # If vector is provided, add to FAISS index
        if study.vector:
            vector = np.array([study.vector]).astype("float32")
            index.add(vector)
        
        return {
            "message": "Study saved successfully",
            "id": str(result.inserted_id)
        }
    except Exception as e:
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search")
def search_vectors(query_vector: list):
   query = np.array([query_vector]).astype("float32")
   distances, indices = index.search(query, k=5)
   return {"distances": distances.tolist(), "indices": indices.tolist()}

@app.get("/")
def read_root():
  return {"message": "Welcome to the KYS RAG: Science Decoder Tool!"}

@app.post("/ask")
def answer_question(request: QuestionRequest):
  inputs = tokenizer(request.question, request.context, return_tensors="pt", truncation=True, max_length=512)
  outputs = model(**inputs)

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
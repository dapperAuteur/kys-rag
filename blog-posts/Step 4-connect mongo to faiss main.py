from fastapi import FastAPI
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from pymongo import MongoClient
from pydantic import BaseModel
import torch

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["science_decoder"]
studies_collection = db["studies"]

# Hugging Face SciBERT setup
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModelForQuestionAnswering.from_pretrained("allenai/scibert_scivocab_uncased")

# Initialize FAISS index
index = faiss.IndexFlatL2(768)

# Load existing embeddings from MongoDB
existing_studies = studies_collection.find()
embeddings = []
for study in existing_studies:
    if "embedding" in study:
        embeddings.append(study["embedding"])

if embeddings:
    index.add(np.array(embeddings, dtype="float32"))

# Define FastAPI app
app = FastAPI()

class Study(BaseModel):
    title: str
    text: str
    topic: str
    discipline: str
    embedding: list = None  # Optional for when not manually provided

class QuestionRequest(BaseModel):
    question: str
    context: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Science Decoder Tool!"}

@app.post("/save-study")
def save_study(study: Study):
    # Generate embedding for the study text
    inputs = tokenizer(study.text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        embedding = model(**inputs).last_hidden_state.mean(dim=1).squeeze().tolist()
    
    study_data = {
        "title": study.title,
        "text": study.text,
        "topic": study.topic,
        "discipline": study.discipline,
        "embedding": embedding
    }
    result = studies_collection.insert_one(study_data)
    index.add(np.array([embedding], dtype="float32"))  # Add to FAISS index
    return {"message": "Study saved", "id": str(result.inserted_id)}

@app.get("/get-studies/{topic}")
def get_studies_by_topic(topic: str):
    studies = list(studies_collection.find({"topic": topic}))
    for study in studies:
        study["_id"] = str(study["_id"])  # Convert ObjectId to string
    return {"studies": studies}

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

@app.post("/search-studies")
def search_studies(query_text: str):
    # Generate embedding for the query
    inputs = tokenizer(query_text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        query_embedding = model(**inputs).last_hidden_state.mean(dim=1).squeeze().numpy()
    
    # Search FAISS for similar embeddings
    distances, indices = index.search(np.array([query_embedding], dtype="float32"), k=5)
    
    # Fetch studies from MongoDB using the indices
    results = []
    for idx in indices[0]:
        if idx < studies_collection.count_documents({}):
            results.append(studies_collection.find_one({}, skip=idx))
    
    # Convert ObjectIds to strings
    for result in results:
        result["_id"] = str(result["_id"])
    
    return {"results": results}

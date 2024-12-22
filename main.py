from fastapi import FastAPI
import faiss
import numpy as np
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from pydantic import BaseModel
import torch

class QuestionRequest(BaseModel):
    question: str
    context: str

tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoModelForQuestionAnswering.from_pretrained("allenai/scibert_scivocab_uncased")

index = faiss.IndexFlatL2(768)

# Example: Add random data to the index
data = np.random.random((10, 768)).astype("float32")
index.add(data)

app = FastAPI()

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
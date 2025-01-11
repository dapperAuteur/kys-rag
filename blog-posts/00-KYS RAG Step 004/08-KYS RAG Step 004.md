# Modernizing Your Vector Search Application: From FAISS to MongoDB with Motor

When building modern applications, sometimes we need to change our technology choices to make things work better. Today, I'll walk you through how to improve a scientific paper search application by making two important changes:

1. Moving from FAISS to MongoDB for vector storage and search
2. Switching from PyMongo to Motor for better async support

## Why Make These Changes?

Imagine you're building a house. Sometimes you realize that the wood you chose isn't working well, so you switch to brick. That's similar to what we're doing here - we're switching from FAISS (the wood) to MongoDB (the brick) for storing our special number patterns (vectors). We're also upgrading our tools by switching from PyMongo to Motor, which helps our application work faster.

## The New Design

Our improved application will:
- Store scientific papers and their vector representations in MongoDB
- Use Motor for fast, non-blocking database operations
- Perform vector similarity search directly in MongoDB
- Include type checking to catch errors early
- Add testing at each step to make sure everything works

Let's break this down into manageable pieces.

## Step 1: Setting Up Our Types

First, let's create clear definitions for our data using Pydantic models:

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class PydanticObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

class Study(BaseModel):
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    text: str
    topic: str
    discipline: str
    vector: List[float]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class SearchQuery(BaseModel):
    query_text: str
    limit: int = 5
```

## Step 2: Database Connection with Motor

Here's how we set up our database connection using Motor:

```python
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from functools import lru_cache

class DatabaseManager:
    def __init__(self, mongodb_url: str):
        self.client: Optional[AsyncIOMotorClient] = None
        self.mongodb_url = mongodb_url

    async def connect(self):
        self.client = AsyncIOMotorClient(self.mongodb_url)
        await self.client.admin.command('ping')  # Test the connection
        return self.client

    async def close(self):
        if self.client:
            self.client.close()

    @property
    def db(self):
        return self.client.science_decoder

@lru_cache()
def get_database() -> DatabaseManager:
    return DatabaseManager(os.getenv("MONGODB_URL", "mongodb://localhost:27017"))
```

## Step 3: Creating Our Service Layer

The service layer handles our business logic:

```python
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from typing import List, Tuple, Dict, Any

class StudyService:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
        self.model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")

    async def generate_embedding(self, text: str) -> List[float]:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            return embedding.tolist()

    async def save_study(self, study: Study) -> str:
        study.vector = await self.generate_embedding(study.text)
        result = await self.db.db.studies.insert_one(study.dict(by_alias=True))
        return str(result.inserted_id)

    async def search_similar_studies(self, query: SearchQuery) -> List[Study]:
        query_vector = await self.generate_embedding(query.query_text)
        
        pipeline = [
            {
                "$search": {
                    "index": "vector_index",  # Create this index in MongoDB
                    "knnBeta": {
                        "vector": query_vector,
                        "path": "vector",
                        "k": query.limit
                    }
                }
            },
            {
                "$project": {
                    "vector": 0,  # Exclude vector from results
                    "score": {"$meta": "searchScore"}
                }
            }
        ]

        results = []
        async for doc in self.db.db.studies.aggregate(pipeline):
            results.append(Study(**doc))
        return results
```

## Step 4: FastAPI Endpoints

Now let's create our API endpoints:

```python
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager

async def lifespan(app: FastAPI):
    db = get_database()
    await db.connect()
    yield
    await db.close()

app = FastAPI(lifespan=lifespan)

@app.post("/studies/", response_model=dict)
async def create_study(
    study: Study,
    service: StudyService = Depends(get_study_service)
):
    try:
        study_id = await service.save_study(study)
        return {"id": study_id, "message": "Study saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/", response_model=List[Study])
async def search_studies(
    query: SearchQuery,
    service: StudyService = Depends(get_study_service)
):
    try:
        results = await service.search_similar_studies(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Testing Our Application

Let's create tests to make sure everything works correctly:

```python
import pytest
from httpx import AsyncClient
import numpy as np

@pytest.fixture
async def test_app():
    # Use test database URL
    app.dependency_overrides[get_database] = lambda: DatabaseManager(
        "mongodb://localhost:27017/test_db"
    )
    return app

@pytest.fixture
async def async_client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

async def test_create_study(async_client):
    study_data = {
        "title": "Test Study",
        "text": "This is a test study about science.",
        "topic": "Testing",
        "discipline": "Computer Science"
    }
    
    response = await async_client.post("/studies/", json=study_data)
    assert response.status_code == 200
    assert "id" in response.json()

async def test_search_studies(async_client):
    # First create a study
    study_data = {
        "title": "Test Study",
        "text": "This is a test study about science.",
        "topic": "Testing",
        "discipline": "Computer Science"
    }
    await async_client.post("/studies/", json=study_data)

    # Then search for it
    search_data = {
        "query_text": "test study science",
        "limit": 5
    }
    response = await async_client.post("/search/", json=search_data)
    assert response.status_code == 200
    assert len(response.json()) > 0
```

## Setting Up MongoDB Vector Search

To enable vector search in MongoDB, you'll need to create an index. Connect to your MongoDB database and run:

```javascript
db.studies.createIndex(
  { vector: "vector" },
  { 
    name: "vector_index",
    vectorSearchOptions: {
      numDimensions: 768,
      similarity: "cosine"
    }
  }
)
```

## Running the Application

1. Install dependencies:
```bash
pip install fastapi uvicorn motor pydantic transformers torch pytest httpx
```

2. Set up your environment variables:
```bash
export MONGODB_URL="mongodb://localhost:27017"
```

3. Run the application:
```bash
uvicorn main:app --reload
```

4. Run tests:
```bash
pytest tests/ -v
```

## Key Benefits of This Refactor

1. **Simpler Architecture**: By removing FAISS, we've eliminated a complex component and consolidated our vector storage in MongoDB.
2. **Better Performance**: Motor's async support means our application can handle more requests without blocking.
3. **Type Safety**: Pydantic models help catch errors before they reach production.
4. **Easier Testing**: Our modular design makes it simple to test each component.
5. **Improved Maintainability**: Clear separation of concerns makes the code easier to understand and modify.

## Next Steps

To further improve the application, consider:
1. Adding monitoring and logging
2. Implementing caching for frequently accessed studies
3. Adding authentication and authorization
4. Creating a backup strategy for your MongoDB data

Remember to monitor your MongoDB performance and adjust the vector search index settings based on your specific needs.
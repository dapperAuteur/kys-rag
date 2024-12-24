from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Optional
import logging
from models import Study, SearchQuery, SearchResponse
from database import database
from config import get_settings
from bson import ObjectId

logger = logging.getLogger(__name__)

class StudyService:
    """Handles business logic for study operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.tokenizer = AutoTokenizer.from_pretrained(self.settings.MODEL_NAME)
        self.model = AutoModel.from_pretrained(self.settings.MODEL_NAME)
        
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for text"""
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
                return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def save_study(self, study: Study) -> str:
        """Save study with generated vector embedding"""
        try:
            # Generate vector embedding if not provided
            if not study.vector:
                study.vector = await self.generate_embedding(study.text)
            
            # Convert the study to a dictionary, excluding None values
            document = study.model_dump(by_alias=True, exclude_none=True)
            
            # Remove id/_id if it's None
            if "_id" in document and document["_id"] is None:
                del document["_id"]

            # Insert into database
            result = await database.db.studies.insert_one(document)

            # Log the generated _id to confirm it exists
            logger.info(f"Study saved successfully with ID result.inserted_id: {result.inserted_id}")
            logger.info(f"Study saved successfully with ID study.id: {study.id}")

            # Return the _id as a string
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving study: {e}")
            raise

    async def search_similar_studies(
        self,
        query: SearchQuery
    ) -> List[SearchResponse]:
        """Search for similar studies using vector similarity"""
        try:
            # Generate query vector
            query_vector = await self.generate_embedding(query.query_text)
            
            # Perform similarity search
            results = await database.vector_similarity_search(
                query_vector=query_vector,
                limit=query.limit
            )
            
            # Convert results to response objects
            response_results = []
            for doc in results:
                score = doc.pop("score", 0.0)
                if score >= query.min_score:
                    study = Study(**doc)
                    response_results.append(SearchResponse(study=study, score=score))
            
            return response_results
        except Exception as e:
            logger.error(f"Error searching studies: {e}")
            raise

    async def get_study_by_id(self, study_id: str) -> Optional[Study]:
        """Retrieve a study by its ID"""
        try:
            # Convert string ID to ObjectId for MongoDB query
            doc = await database.db.studies.find_one({"_id": ObjectId(study_id)})
            if doc:
                # Convert ObjectId to string before creating Study object
                doc["_id"] = str(doc["_id"])
                return Study(**doc)
            return None
        except Exception as e:
            logger.error(f"Error retrieving study: {e}")
            raise
        
# test_main.py changes for the failing tests
def test_create_and_retrieve_study(test_client):
    """Test study creation and retrieval"""
    study_data = {
        "title": "Test Study",
        "text": "This is a test study about science.",
        "topic": "Testing",
        "discipline": "Computer Science",
        "vector": []  # Add empty vector if required
    }
    
    # Create study
    response = test_client.post("/studies/", json=study_data)
    assert response.status_code == 200
    data = response.json()
    assert "details" in data
    study_id = data["details"]["id"]
    
    # Retrieve study - add small delay if needed
    response = test_client.get(f"/studies/{study_id}")
    assert response.status_code == 200
    study = response.json()
    assert study["title"] == study_data["title"]

def test_search_studies(test_client):
    """Test vector similarity search"""
    # Create test studies
    study_data = [
        {
            "title": "AI Study",
            "text": "This study focuses on artificial intelligence.",
            "topic": "AI",
            "discipline": "Computer Science",
            "vector": []  # Add empty vector if required
        },
        {
            "title": "Biology Study",
            "text": "This study examines cell biology.",
            "topic": "Biology",
            "discipline": "Life Sciences",
            "vector": []  # Add empty vector if required
        }
    ]
    
    # Create studies and store their IDs
    study_ids = []
    for data in study_data:
        response = test_client.post("/studies/", json=data)
        assert response.status_code == 200
        study_ids.append(response.json()["details"]["id"])
    
    # Search for AI-related studies
    search_query = {
        "query_text": "artificial intelligence research",
        "limit": 5,
        "min_score": 0.0
    }
    
    response = test_client.post("/search/", json=search_query)
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0

study_service = StudyService()
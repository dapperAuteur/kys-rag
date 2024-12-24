from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Optional
import logging
from models import Study, SearchQuery, SearchResponse
from database import database
from config import get_settings

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
            
            # Insert into database
            result = await database.db.studies.insert_one(
                study.model_dump(by_alias=True)
            )
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
            doc = await database.db.studies.find_one({"_id": study_id})
            return Study(**doc) if doc else None
        except Exception as e:
            logger.error(f"Error retrieving study: {e}")
            raise

study_service = StudyService()
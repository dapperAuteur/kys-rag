from transformers import AutoTokenizer, AutoModel
import torch
from typing import List, Optional
import logging
import numpy as np
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
                # Normalize the embedding
                normalized = embedding / torch.norm(embedding)
                return normalized.tolist()
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

            # Get database instance and insert document
            db = await database.get_database()
            result = await db.studies.insert_one(document)
            
            logger.info(f"Study saved successfully with ID: {result.inserted_id}")
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
            # Generate query vector and normalize it
            query_vector = await self.generate_embedding(query.query_text)
            
            # Get database instance
            db = await database.get_database()
            
            # Perform vector similarity search using aggregation pipeline
            pipeline = [
                {
                    "$addFields": {
                        "similarity": {
                            "$let": {
                                "vars": {
                                    "dotProduct": {
                                        "$reduce": {
                                            "input": {"$zip": {"inputs": ["$vector", query_vector]}},
                                            "initialValue": 0.0,
                                            "in": {
                                                "$add": [
                                                    "$$value",
                                                    {"$multiply": [
                                                        {"$arrayElemAt": ["$$this", 0]},
                                                        {"$arrayElemAt": ["$$this", 1]}
                                                    ]}
                                                ]
                                            }
                                        }
                                    }
                                },
                                "in": {
                                    "$min": [1.0, {"$max": [0.0, "$$dotProduct"]}]
                                }
                            }
                        }
                    }
                },
                {"$match": {"similarity": {"$gte": query.min_score}}},
                {"$sort": {"similarity": -1}},
                {"$limit": query.limit}
            ]
            
            results = []
            async for doc in db.studies.aggregate(pipeline):
                score = doc.pop("similarity", 0.0)
                if score >= query.min_score:
                    study = Study(**doc)
                    results.append(SearchResponse(study=study, score=score))
            
            return results
        except Exception as e:
            logger.error(f"Error searching studies: {e}")
            raise

    async def get_study_by_id(self, study_id: str) -> Optional[Study]:
        """Retrieve a study by its ID"""
        try:
            db = await database.get_database()
            doc = await db.studies.find_one({"_id": ObjectId(study_id)})
            if doc:
                return Study(**doc)
            return None
        except Exception as e:
            logger.error(f"Error retrieving study: {e}")
            raise

# Create singleton instance
study_service = StudyService()
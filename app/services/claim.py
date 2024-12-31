from typing import List, Optional, Dict, Tuple
import logging
from app.models.models import Claim, ScientificStudy
from app.core.database import database, Collection
from .scientific_study import scientific_study_service
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from datetime import datetime

logger = logging.getLogger(__name__)

class ClaimService:
    """Service for handling scientific claim verification."""
    
    def __init__(self):
        """Initialize the claim verification service."""
        self.settings = database.settings
        self.tokenizer = AutoTokenizer.from_pretrained(self.settings.MODEL_NAME)
        self.verifier_model = AutoModelForSequenceClassification.from_pretrained(
            self.settings.MODEL_NAME,
            num_labels=2  # support/contradict
        )
    
    async def extract_claims(self, text: str) -> List[Claim]:
        """Extract scientific claims from text."""
        # This is a placeholder for more sophisticated claim extraction
        # In a real implementation, you might use a fine-tuned model
        sentences = text.split('.')
        claims = []
        
        for sentence in sentences:
            # Simple heuristic: look for scientific statement indicators
            indicators = [
                "study shows", "research indicates", "scientists found",
                "according to research", "evidence suggests",
                "results demonstrate", "analysis reveals"
            ]
            
            if any(indicator in sentence.lower() for indicator in indicators):
                claims.append(Claim(
                    text=sentence.strip(),
                    confidence_score=0.0,
                    verified=False
                ))
        
        return claims

    async def verify_claim(
        self,
        claim: Claim,
        scientific_studies: List[ScientificStudy]
    ) -> Tuple[bool, float, str]:
        """Verify a claim against scientific studies."""
        try:
            best_confidence = 0.0
            verification_notes = []
            claim_verified = False
            
            # Compare claim against each study
            for study in scientific_studies:
                # Prepare input for the model
                inputs = self.tokenizer(
                    claim.text,
                    study.text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding=True
                )
                
                # Get model prediction
                with torch.no_grad():
                    outputs = self.verifier_model(**inputs)
                    probabilities = torch.softmax(outputs.logits, dim=1)
                    support_score = probabilities[0][1].item()
                
                # Update confidence if this is the best match
                if support_score > best_confidence:
                    best_confidence = support_score
                    
                # Add supporting evidence to notes
                if support_score > self.settings.MIN_CLAIM_CONFIDENCE:
                    claim_verified = True
                    verification_notes.append(
                        f"Supported by {study.title} (confidence: {support_score:.2f})"
                    )
            
            # Compile final verification notes
            final_notes = "\n".join(verification_notes) if verification_notes else \
                         "No strong supporting evidence found in provided studies."
            
            return claim_verified, best_confidence, final_notes

        except Exception as e:
            logger.error(f"Error verifying claim: {e}")
            raise

    async def find_relevant_studies(
        self,
        claim: Claim,
        limit: int = 5
    ) -> List[ScientificStudy]:
        """Find scientific studies relevant to a claim."""
        try:
            search_results = await scientific_study_service.search_similar_studies(
                query_text=claim.text,
                limit=limit,
                min_score=self.settings.MIN_SIMILARITY_SCORE
            )
            
            return [result.content for result in search_results]
        except Exception as e:
            logger.error(f"Error finding relevant studies: {e}")
            raise

    async def process_claim(self, claim: Claim) -> Claim:
        """Process a claim by finding relevant studies and verifying it."""
        try:
            # Find relevant studies
            relevant_studies = await self.find_relevant_studies(claim)
            
            if not relevant_studies:
                claim.verification_notes = "No relevant scientific studies found."
                claim.confidence_score = 0.0
                claim.verified = False
                return claim
            
            # Verify claim against found studies
            verified, confidence, notes = await self.verify_claim(claim, relevant_studies)
            
            # Update claim with verification results
            claim.verified = verified
            claim.confidence_score = confidence
            claim.verification_notes = notes
            claim.verified_at = datetime.utcnow()
            claim.related_scientific_study_ids = [
                study.id for study in relevant_studies
            ]
            
            return claim
        except Exception as e:
            logger.error(f"Error processing claim: {e}")
            raise

# Create singleton instance
claim_service = ClaimService()
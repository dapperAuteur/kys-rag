# Making Sure Science News is True: A Deep Dive into Claim Processing

When you read a headline like "Scientists Say Coffee Makes You Live Forever!", how do you know if it's true? In our science checking tool, we use a special system called Claim Processing to figure this out. Today, we'll explore how this system works and how we're making it better at catching false or misleading claims about science.

## Understanding Scientific Claims

Think of a scientific claim like a puzzle piece. To know if it fits, we need to:
1. Understand what the claim is saying
2. Find the original research it's talking about
3. Check if the claim matches what the research actually found
4. Look for other research that confirms or contradicts it

Let's see how we build a system to do all this:

```python
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
from transformers import pipeline
import spacy
from app.models.models import Claim, ScientificStudy
from app.services.vector_service import vector_service
from app.core.database import database

@dataclass
class ClaimAnalysis:
    """Stores our detailed analysis of a scientific claim"""
    original_text: str
    verified: bool
    confidence_score: float
    supporting_studies: List[str]
    contradicting_studies: List[str]
    context: str
    verification_notes: List[str]
    analysis_date: datetime

class ClaimProcessor:
    """Helps check if scientific claims are true"""
    
    def __init__(self):
        """Set up our fact-checking tools"""
        # Load our language understanding model
        self.nlp = spacy.load("en_core_sci_lg")
        
        # Set up our scientific claim detector
        self.claim_detector = pipeline(
            "text-classification",
            model="scientific-claim-detector"
        )
        
        # Create our certainty analyzer
        self.certainty_analyzer = pipeline(
            "text-classification",
            model="scientific-certainty-analyzer"
        )
        
        # Set up logging
        self.logger = logging.getLogger(__name__)

    async def identify_claims(self, text: str) -> List[Claim]:
        """Find scientific claims in text"""
        try:
            # Break text into sentences
            doc = self.nlp(text)
            potential_claims = []
            
            # Look at each sentence
            for sent in doc.sents:
                # Check if it looks like a scientific claim
                claim_score = self._evaluate_claim_likelihood(sent.text)
                
                if claim_score > 0.7:  # If it's probably a claim
                    # Create a new claim object
                    claim = Claim(
                        text=sent.text,
                        context=self._get_surrounding_context(doc, sent),
                        location_in_text={
                            "start": sent.start_char,
                            "end": sent.end_char
                        }
                    )
                    potential_claims.append(claim)
            
            return potential_claims
            
        except Exception as e:
            self.logger.error(f"Error identifying claims: {e}")
            raise

    async def process_claim(self, claim: Claim) -> ClaimAnalysis:
        """Check if a scientific claim is true"""
        try:
            # Start keeping track of what we find
            verification_notes = []
            
            # Step 1: Validate the claim structure
            claim = await self._validate_claim(claim)
            
            # Step 2: Find relevant scientific papers
            relevant_studies = await self._find_supporting_studies(claim)
            
            # Step 3: Look for opposing evidence
            contradicting_studies = await self._find_contradicting_studies(claim)
            
            # Step 4: Check how certain the claim is
            certainty_level = await self._analyze_certainty(claim.text)
            verification_notes.append(
                f"Claim certainty level: {certainty_level}"
            )
            
            # Step 5: Cross-reference with other claims
            related_claims = await self._find_related_claims(claim)
            
            # Put together our final analysis
            analysis = ClaimAnalysis(
                original_text=claim.text,
                verified=len(relevant_studies) > 0,
                confidence_score=self._calculate_confidence(
                    relevant_studies,
                    contradicting_studies,
                    certainty_level
                ),
                supporting_studies=[study.doi for study in relevant_studies],
                contradicting_studies=[study.doi for study in contradicting_studies],
                context=claim.context,
                verification_notes=verification_notes,
                analysis_date=datetime.utcnow()
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error processing claim: {e}")
            raise

    async def _validate_claim(self, claim: Claim) -> Claim:
        """Make sure the claim is properly formed"""
        if not claim.text:
            raise ValueError("Claim text is required")
            
        # Clean up the text
        claim.text = claim.text.strip()
        
        # Make sure it's not too short or too long
        if len(claim.text) < 10 or len(claim.text) > 1000:
            raise ValueError("Claim text must be between 10 and 1000 characters")
            
        return claim

    async def _find_supporting_studies(
        self,
        claim: Claim
    ) -> List[ScientificStudy]:
        """Find scientific papers that support this claim"""
        try:
            # Get similar papers using our vector search
            similar_studies = await vector_service.find_similar_content(
                claim.text,
                collection="scientific_studies",
                min_similarity=0.7
            )
            
            # Check each paper more carefully
            supporting_studies = []
            for study in similar_studies:
                support_score = await self._analyze_support_level(
                    claim.text,
                    study.text
                )
                
                if support_score > 0.8:  # If it strongly supports the claim
                    supporting_studies.append(study)
            
            return supporting_studies
            
        except Exception as e:
            self.logger.error(f"Error finding supporting studies: {e}")
            raise

    async def _find_contradicting_studies(
        self,
        claim: Claim
    ) -> List[ScientificStudy]:
        """Find scientific papers that might contradict this claim"""
        try:
            # Look for papers with opposite findings
            contradicting_papers = await vector_service.find_opposing_content(
                claim.text,
                collection="scientific_studies",
                min_similarity=0.7
            )
            
            # Verify that they really contradict
            verified_contradictions = []
            for paper in contradicting_papers:
                contradiction_score = await self._analyze_contradiction_level(
                    claim.text,
                    paper.text
                )
                
                if contradiction_score > 0.8:  # If it strongly contradicts
                    verified_contradictions.append(paper)
            
            return verified_contradictions
            
        except Exception as e:
            self.logger.error(f"Error finding contradicting studies: {e}")
            raise

    async def _analyze_certainty(self, text: str) -> float:
        """Check how certain a claim is about its findings"""
        try:
            # Look for words that show uncertainty
            uncertainty_markers = [
                "may", "might", "could", "suggests",
                "potentially", "possibly", "appears to"
            ]
            
            # Look for words that show strong certainty
            certainty_markers = [
                "proves", "demonstrates", "shows",
                "confirms", "establishes", "definitely"
            ]
            
            # Calculate certainty score
            text_lower = text.lower()
            uncertainty_count = sum(
                text_lower.count(marker) 
                for marker in uncertainty_markers
            )
            certainty_count = sum(
                text_lower.count(marker) 
                for marker in certainty_markers
            )
            
            # Return a score between 0 and 1
            total = uncertainty_count + certainty_count
            if total == 0:
                return 0.5  # Neutral if no markers found
                
            return certainty_count / total
            
        except Exception as e:
            self.logger.error(f"Error analyzing certainty: {e}")
            raise

    def _calculate_confidence(
        self,
        supporting: List[ScientificStudy],
        contradicting: List[ScientificStudy],
        certainty: float
    ) -> float:
        """Figure out how confident we are about our verification"""
        try:
            # Start with a base score
            confidence = 0.5
            
            # Add points for supporting studies
            confidence += len(supporting) * 0.1
            
            # Subtract points for contradicting studies
            confidence -= len(contradicting) * 0.15
            
            # Adjust based on certainty
            confidence *= certainty
            
            # Keep score between 0 and 1
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            raise

```

## How Our Claim Checker Works

Let's break down the important parts of our system:

### 1. Finding Claims in Text
First, we need to spot when an article is making a scientific claim:

```python
async def identify_claims(self, text: str) -> List[Claim]:
```

This is like having a very careful reader who:
- Reads each sentence
- Looks for signs that it's making a scientific statement
- Marks these sentences for checking

### 2. Understanding the Claim
Once we find a claim, we need to understand what it's saying:

```python
async def _analyze_certainty(self, text: str) -> float:
```

This part:
- Checks how strong the claim is ("might help" vs "definitely cures")
- Looks for important scientific terms
- Understands what kind of evidence it's talking about

### 3. Finding Evidence
We then look for scientific papers that talk about this topic:

```python
async def _find_supporting_studies(
    self,
    claim: Claim
) -> List[ScientificStudy]:
```

This is like a librarian who:
- Finds papers about the same topic
- Checks if they actually support the claim
- Rates how strong the support is

### 4. Looking for Contradictions
We also look for papers that might disagree:

```python
async def _find_contradicting_studies(
    self,
    claim: Claim
) -> List[ScientificStudy]:
```

This helps us:
- Find different viewpoints
- Understand scientific debates
- Give a more complete picture

## Making Sure We're Right

Our system uses several checks to make sure we're giving good information:

### 1. Confidence Scoring
We calculate how sure we are about our verification:

```python
def _calculate_confidence(
    self,
    supporting: List[ScientificStudy],
    contradicting: List[ScientificStudy],
    certainty: float
) -> float:
```

This looks at:
- How many papers support the claim
- How many papers disagree
- How certain the claim is
- How well-respected the papers are

### 2. Context Checking
We look at the full context of claims:

```python
context=self._get_surrounding_context(doc, sent)
```

This helps us:
- Understand what the article is really saying
- Catch if context changes the meaning
- See if important details were left out

## Real-World Example

Let's see how this works with a real example:

Article claim: "Coffee drinking adds 10 years to your life!"

Our system would:
1. Identify this as a scientific claim
2. Note it's a very strong claim (100% certainty stated)
3. Look for studies about coffee and longevity
4. Probably find that:
   - Some studies show coffee has health benefits
   - No studies show such a dramatic effect
   - The claim is exaggerating real research

Final result might be:
```python
ClaimAnalysis(
    verified=False,
    confidence_score=0.85,
    verification_notes=[
        "Related studies show modest positive effects",
        "No evidence for 10-year claim",
        "Exaggeration of actual research findings"
    ]
)
```

## What's Next?

We're working on making our claim checker even better by:
1. Adding more sophisticated language understanding
2. Improving our certainty analysis
3. Making it better at handling complex scientific concepts
4. Adding checks for statistical accuracy

In our next post, we'll look at how we test our claim processing system and make sure it's giving reliable results. We'll also explore how we can make it work faster without losing accuracy.

Remember, good fact-checking takes time and careful attention to detail. By building these checks into our system, we help people understand science news more accurately!

# Keeping Track of the Details with MongoDB: Adding Rich Metadata to Your Scientific Paper Search

Imagine you're organizing a huge library of scientific papers. You need a way to keep track of not just the papers themselves, but also important details about them - like when they were added, who wrote them, and what they're about. That's exactly what we'll do today by adding metadata storage to our scientific paper search application.

## Why MongoDB?

Before we dive in, let's talk about why MongoDB is a great choice for beginners:

1. It's free to start with - MongoDB has a generous free tier that's perfect for learning
2. It's easy to set up - you can be up and running in minutes
3. It works like a smart filing cabinet - storing information in a way that's easy to understand
4. It's flexible - you can add new types of information without rebuilding everything

## Getting Started

First, let's install MongoDB on your computer. We'll use MongoDB Community Edition:

### For Windows:
1. Download the MongoDB Community Server from mongodb.com/try/download/community
2. Run the installer and follow the prompts
3. MongoDB will install as a service and start automatically

### For Mac (using Homebrew):
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### For Linux (Ubuntu):
```bash
sudo apt-get update
sudo apt-get install -y mongodb
sudo systemctl start mongodb
```

## Enhancing Our Data Model

We'll update our models to include more metadata about each study. Here's what we'll add to our existing code:

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

class Author(BaseModel):
    """Represents an author of a scientific study"""
    name: str
    email: Optional[EmailStr] = None
    institution: Optional[str] = None

class Study(BaseModel):
    """Enhanced study model with metadata"""
    id: Optional[PydanticObjectId] = Field(None, alias="_id")
    title: str
    text: str
    topic: str
    discipline: str
    vector: Optional[List[float]] = None
    
    # New metadata fields
    authors: List[Author]
    publication_date: Optional[datetime] = None
    keywords: List[str] = Field(default_factory=list)
    citation_count: int = 0
    doi: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "AI in Healthcare",
                "text": "A study about artificial intelligence applications in healthcare",
                "topic": "AI Healthcare",
                "discipline": "Computer Science",
                "authors": [
                    {
                        "name": "Jane Smith",
                        "email": "jane.smith@university.edu",
                        "institution": "University Research Center"
                    }
                ],
                "keywords": ["AI", "healthcare", "machine learning"],
                "doi": "10.1234/example.doi"
            }
        }
```

## Updating Our Database Layer

We'll enhance our database manager to handle the new metadata:

```python
async def setup_indexes(self) -> None:
    """Create necessary database indexes including metadata"""
    try:
        # Existing vector search index setup...
        
        # Create indexes for metadata searches
        await self.db.studies.create_index([
            ("title", "text"),
            ("text", "text"),
            ("topic", "text"),
            ("keywords", "text")
        ], name="text_search_index")
        
        # Create indexes for common queries
        await self.db.studies.create_index([("publication_date", -1)])
        await self.db.studies.create_index([("citation_count", -1)])
        await self.db.studies.create_index([("doi", 1)], unique=True, sparse=True)
        await self.db.studies.create_index([("created_at", -1)])
        
        logger.info("All indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        raise
```

## Adding Search Capabilities

Let's update our search functionality to use the new metadata:

```python
class SearchQuery(BaseModel):
    """Enhanced search query with metadata filters"""
    query_text: str
    limit: int = 10
    min_score: float = 0.5
    discipline: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_citations: Optional[int] = None
    keywords: Optional[List[str]] = None

async def search_studies(
    self,
    query: SearchQuery
) -> List[dict]:
    """Search studies with metadata filtering"""
    try:
        # Build the search pipeline
        pipeline = []
        
        # Vector similarity search stage
        pipeline.append({
            "$search": {
                "index": "vector_index",
                "knnBeta": {
                    "vector": await self.generate_embedding(query.query_text),
                    "path": "vector",
                    "k": query.limit * 2  # Get more results for filtering
                }
            }
        })
        
        # Apply metadata filters
        match_stage = {"$match": {}}
        
        if query.discipline:
            match_stage["$match"]["discipline"] = query.discipline
            
        if query.date_from or query.date_to:
            date_filter = {}
            if query.date_from:
                date_filter["$gte"] = query.date_from
            if query.date_to:
                date_filter["$lte"] = query.date_to
            match_stage["$match"]["publication_date"] = date_filter
            
        if query.min_citations:
            match_stage["$match"]["citation_count"] = {"$gte": query.min_citations}
            
        if query.keywords:
            match_stage["$match"]["keywords"] = {"$all": query.keywords}
            
        if match_stage["$match"]:
            pipeline.append(match_stage)
            
        # Limit results and exclude vector field
        pipeline.extend([
            {"$limit": query.limit},
            {
                "$project": {
                    "vector": 0,
                    "score": {"$meta": "searchScore"}
                }
            }
        ])
        
        results = await self.db.studies.aggregate(pipeline).to_list(length=query.limit)
        return results
    except Exception as e:
        logger.error(f"Error in search_studies: {e}")
        raise
```

## Testing Our Enhanced System

Let's add some tests to verify our metadata handling:

```python
def test_create_study_with_metadata(test_client):
    """Test creation of a study with full metadata"""
    study_data = {
        "title": "Test Study",
        "text": "This is a test study about science.",
        "topic": "Testing",
        "discipline": "Computer Science",
        "authors": [
            {
                "name": "Test Author",
                "email": "test@example.com",
                "institution": "Test University"
            }
        ],
        "keywords": ["test", "science", "metadata"],
        "doi": "10.1234/test.12345"
    }
    
    response = test_client.post("/studies/", json=study_data)
    assert response.status_code == 200
    data = response.json()
    assert "details" in data
    study_id = data["details"]["id"]
    
    # Verify the stored study
    response = test_client.get(f"/studies/{study_id}")
    assert response.status_code == 200
    study = response.json()
    assert study["title"] == study_data["title"]
    assert study["authors"][0]["name"] == study_data["authors"][0]["name"]
    assert study["doi"] == study_data["doi"]

def test_metadata_search(test_client):
    """Test searching with metadata filters"""
    # Create test studies with different metadata
    studies = [
        {
            "title": "AI Study 2024",
            "text": "Recent developments in AI",
            "topic": "AI",
            "discipline": "Computer Science",
            "authors": [{"name": "AI Researcher"}],
            "publication_date": "2024-01-01T00:00:00Z",
            "keywords": ["AI", "machine learning"],
            "citation_count": 100
        },
        {
            "title": "Biology Study 2023",
            "text": "Advanced biology research",
            "topic": "Biology",
            "discipline": "Life Sciences",
            "authors": [{"name": "Biology Researcher"}],
            "publication_date": "2023-01-01T00:00:00Z",
            "keywords": ["biology", "research"],
            "citation_count": 50
        }
    ]
    
    for study in studies:
        response = test_client.post("/studies/", json=study)
        assert response.status_code == 200
    
    # Test search with metadata filters
    search_query = {
        "query_text": "research",
        "discipline": "Computer Science",
        "date_from": "2024-01-01T00:00:00Z",
        "min_citations": 75,
        "keywords": ["AI"]
    }
    
    response = test_client.post("/search/", json=search_query)
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert all(r["discipline"] == "Computer Science" for r in results)
```

## Using the Enhanced System

Let's try out our improved system:

1. Start MongoDB:
```bash
# If not already running
sudo systemctl start mongodb  # Linux
brew services start mongodb-community  # Mac
```

2. Create a new study with rich metadata:
```python
import requests
import json
from datetime import datetime

study = {
    "title": "Machine Learning in Climate Science",
    "text": "This study explores applications of ML in climate prediction...",
    "topic": "Climate Science",
    "discipline": "Environmental Science",
    "authors": [
        {
            "name": "Sarah Johnson",
            "email": "sarah.johnson@climate.edu",
            "institution": "Climate Research Institute"
        }
    ],
    "keywords": ["machine learning", "climate", "prediction"],
    "publication_date": datetime.utcnow().isoformat(),
    "doi": "10.1234/climate.2024.001"
}

response = requests.post("http://localhost:8000/studies/", json=study)
print(json.dumps(response.json(), indent=2))
```

3. Search for studies with metadata filters:
```python
search_query = {
    "query_text": "climate prediction",
    "discipline": "Environmental Science",
    "date_from": "2024-01-01T00:00:00Z",
    "keywords": ["machine learning"]
}

response = requests.post("http://localhost:8000/search/", json=search_query)
results = response.json()
for result in results:
    print(f"\nTitle: {result['title']}")
    print(f"Authors: {', '.join(a['name'] for a in result['authors'])}")
    print(f"Keywords: {', '.join(result['keywords'])}")
```

## Next Steps

Now that we have rich metadata storage, consider:

1. Adding faceted search capabilities
2. Implementing sorting options (by date, citations, etc.)
3. Creating an admin interface for metadata management
4. Setting up periodic updates for citation counts
5. Adding validation for DOIs and other identifiers

Remember to regularly back up your MongoDB database to protect your metadata:

```bash
mongodump --db science_decoder --out /path/to/backup
```

To restore from backup:
```bash
mongorestore --db science_decoder /path/to/backup/science_decoder
```

By adding metadata to our scientific paper search system, we've made it much more powerful and useful. Users can now find papers not just by content similarity, but also by author, date, citation count, and other important attributes. This makes our system more valuable for researchers and easier to maintain for administrators.
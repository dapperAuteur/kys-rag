# Part 5: Organizing Your Science Data with MongoDB

Welcome back, future data organizers! In our last lesson, we learned how to use SciBERT to understand scientific text. Today, we're going to learn how to store and organize all that information using MongoDB.

## What We Learned Last Time
In Part 4, we:
- Set up SciBERT to understand scientific language
- Created embeddings (special number patterns) from scientific text
- Stored these embeddings temporarily in FAISS

## Why We Need MongoDB
Imagine you have a big library. FAISS helps us find similar books quickly, but we need somewhere to store all the book details - like titles, authors, and where to find them. That's where MongoDB comes in! 

MongoDB is like a super-organized librarian that helps us:
1. Keep track of scientific papers and articles separately
2. Store important details about each document
3. Find information quickly when we need it

## What We're Building Today
We'll create a system that:
- Stores scientific papers in one collection
- Stores articles about those papers in another collection
- Links articles to the papers they talk about
- Makes it easy to search everything

## New Project Files

Let's look at the important changes we need to make. We'll store these files in our project folder:

### 1. Updated Configuration (config.py)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017/"
    DATABASE_NAME: str = "science_decoder"
    VECTOR_DIMENSIONS: int = 768
    LOG_LEVEL: str = "INFO"
```

### 2. Updated Database Manager (database.py)
```python
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        logger.info("Connecting to MongoDB...")
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DATABASE_NAME]
        logger.info("Connected successfully!")
```

### 3. Separate Models (models.py)
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class ScientificStudy(BaseModel):
    title: str
    text: str
    authors: List[str]
    publication_date: Optional[datetime] = None
    vector: Optional[List[float]] = None

class Article(BaseModel):
    title: str
    text: str
    url: str
    cited_studies: List[str] = []
    vector: Optional[List[float]] = None
```

## Setting Up MongoDB

1. First, install MongoDB on your computer
2. Create two collections: `studies` and `articles`
3. Set up indexes for fast searching

Here's how to create the indexes in MongoDB:

```javascript
// Create vector search index for studies
db.studies.createIndex(
  { vector: "vector" },
  {
    name: "vector_index",
    vectorSearchOptions: {
      numDimensions: 768,
      similarity: "cosine"
    }
  }
);

// Create text search index for articles
db.articles.createIndex(
  { title: "text", text: "text" }
);
```

## Testing Our Changes

We've added new tests in `test_database.py`:

```python
import pytest
from database import DatabaseManager

async def test_database_connection():
    db = DatabaseManager()
    await db.connect()
    assert db.client is not None
    assert db.db is not None
```

Let's test our new system with some example data:

### 1. Add a Scientific Study
```bash
curl -X POST "http://localhost:8000/studies/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Exercise and Brain Health",
    "text": "Our study shows exercise improves memory",
    "authors": ["Dr. Smith", "Dr. Jones"],
    "publication_date": "2024-01-15T00:00:00Z"
  }'
```

Expected response:
```json
{
  "status": "success",
  "message": "Study saved successfully",
  "id": "507f1f77bcf86cd799439011"
}
```

### 2. Add an Article About the Study
```bash
curl -X POST "http://localhost:8000/articles/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Exercise Makes You Smarter!",
    "text": "Scientists discover exercise helps memory",
    "url": "https://example.com/article",
    "cited_studies": ["507f1f77bcf86cd799439011"]
  }'
```

## What Changed and Why?

1. **Separate Collections**: We split studies and articles into different MongoDB collections because they're different types of content. This makes our code cleaner and searching easier.

2. **Better Types**: We added more type hints and validation to catch errors early. This helps prevent bugs and makes our code more reliable.

3. **More Logging**: We added logging messages to help us (and others) understand what's happening in our code.

## Why These Changes Matter

For hiring managers and companies looking to build similar tools:
- **Scalability**: Our database can handle lots of documents efficiently
- **Reliability**: Type checking and validation prevent common errors
- **Maintainability**: Clear separation of concerns makes the code easier to update
- **Monitoring**: Detailed logging helps track system health

## Coming Up Next
In Part 6, we'll build a chat interface that lets users ask questions about the scientific papers and articles we've stored. We'll use everything we've learned so far to create smart, helpful responses!

Remember: Good organization is the foundation of any successful project. Take your time to understand these concepts - they'll make everything else easier!

Need help? Drop a comment below or check out the full code on GitHub!
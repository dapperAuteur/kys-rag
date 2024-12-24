# Part 5: Keeping Track of the Details with MongoDB - A Step-by-Step Guide

Welcome to Part 5 of our series on building a scientific paper analysis tool. Today, we'll learn how to store and manage scientific papers and articles that reference them. This is an important step in creating a system that can help verify scientific claims made in online articles.

## What We're Building

Imagine you're reading an article about a new scientific discovery. The article mentions several research papers, but how do you know if it's representing them accurately? Our tool will help by:
1. Storing both the article and the research papers it cites
2. Breaking them into smaller pieces for easy searching
3. Keeping track of important details like authors and publication dates
4. Making it easy to compare what the article claims with what the research actually says

## Setting Up Our Project

First, let's install the new packages we need:

```bash
pip install pymupdf beautifulsoup4 requests
```

These packages help us:
- `pymupdf`: Read PDF files
- `beautifulsoup4`: Extract text from web pages
- `requests`: Download web content

## Understanding the Code Changes

Let's walk through the major changes to our code and why we made them.

### 1. Enhanced Data Models

We've updated our models to handle different types of sources. Here's what changed in `models.py`:

```python
class SourceType(str, Enum):
    SCIENTIFIC_STUDY = "scientific_study"
    ARTICLE = "article"

class Source(BaseModel):
    type: SourceType
    url: Optional[HttpUrl] = None
    pdf_path: Optional[str] = None
    title: str
    authors: List[Author]
    citations: List[PydanticObjectId] = []
    text_chunks: List[Dict[str, Union[str, List[float]]]] = []
```

This new structure helps us:
- Track whether something is a scientific study or an article about studies
- Store either a URL or PDF file path
- Keep a list of citations (links between articles and studies)
- Store text in smaller chunks for better searching

### 2. Processing Different Source Types

In `services.py`, we've added new methods to handle both PDFs and web articles:

```python
async def process_source(self, source: Source) -> List[Dict[str, Any]]:
    """Process source content and generate chunks with embeddings"""
    if source.url:
        text = await self._extract_text_from_url(source.url)
    elif source.pdf_path:
        text = await self._extract_text_from_pdf(source.pdf_path)
    else:
        raise ValueError("Source must have either URL or PDF path")
        
    chunks = self._chunk_text(text, chunk_size=512, overlap=50)
    return await self._process_chunks(chunks)
```

This code:
1. Checks if we're dealing with a URL or PDF
2. Extracts the text content
3. Breaks the text into overlapping chunks (like tearing a paper into pieces that slightly overlap)
4. Creates vector embeddings for each chunk

## Testing the New Features

Let's test our changes using both command line and code. We'll create a sample scientific study and an article that cites it.

### 1. Create a Scientific Study

```bash
curl -X POST "http://localhost:8000/studies/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Effects of Exercise on Brain Function",
    "text": "Our research shows regular exercise improves cognitive performance.",
    "topic": "Neuroscience",
    "discipline": "Biology",
    "authors": [{"name": "Dr. Jane Smith"}],
    "source": {
      "type": "scientific_study",
      "pdf_path": "papers/exercise_study.pdf",
      "title": "Exercise and Cognition Study",
      "authors": [{"name": "Dr. Jane Smith"}]
    }
  }'
```

You should see output like:
```json
{
  "status": "success",
  "message": "Study created successfully",
  "details": {"id": "507f1f77bcf86cd799439011"}
}
```

### 2. Create an Article Citing the Study

```bash
curl -X POST "http://localhost:8000/studies/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Exercise Makes You Smarter, Scientists Say",
    "text": "A new study shows exercise boosts brain power.",
    "topic": "Health",
    "discipline": "Science Communication",
    "authors": [{"name": "John Writer"}],
    "source": {
      "type": "article",
      "url": "https://example.com/exercise-article",
      "title": "Exercise and Brain Health",
      "authors": [{"name": "John Writer"}],
      "citations": ["507f1f77bcf86cd799439011"]
    }
  }'
```

### 3. Search for Related Content

```bash
curl -X POST "http://localhost:8000/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "exercise brain cognitive",
    "limit": 5,
    "source_type": "scientific_study",
    "discipline": "Biology"
  }'
```

## Running the Tests

We've created comprehensive tests in `test_main.py`. Run them with:

```bash
python -m pytest tests/ -v
```

The tests will show detailed logs of what's happening:
```
INFO: Setting up test database...
INFO: Testing study creation from PDF...
INFO: Study created with ID: 507f1f77bcf86cd799439011
INFO: Study creation from PDF successful
...
```

## Understanding the Results

When you create or search for content, several things happen:
1. The system extracts text from the source (PDF or webpage)
2. It breaks the text into chunks with some overlap
3. Each chunk gets turned into a vector (like a digital fingerprint)
4. MongoDB stores all this information for quick searching
5. When you search, it finds the most relevant chunks and returns the full documents they belong to

## Next Steps

In Part 6, we'll build a chat interface that lets users:
- Ask questions about stored papers and articles
- Compare what articles claim with the original research
- Get plain-language explanations of scientific concepts

## Setting Up MongoDB Indexes

Before moving on, create these indexes in MongoDB:

```javascript
// For vector search
db.studies.createIndex(
  { "source.text_chunks.vector": "vector" },
  { 
    name: "vector_index",
    vectorSearchOptions: {
      numDimensions: 768,
      similarity: "cosine"
    }
  }
);

// For metadata queries
db.studies.createIndex({ "source.type": 1 });
db.studies.createIndex({ "discipline": 1 });
db.studies.createIndex({ "publication_date": 1 });
```

These indexes help MongoDB find information quickly, like having bookmarks in a large book.

## Common Questions

1. **Why chunk the text?**
   - Breaking text into chunks helps find relevant information more precisely
   - Overlapping chunks maintain context between pieces

2. **Why track citations?**
   - Links articles to their source studies
   - Helps verify if articles accurately represent research

3. **Why use vector search?**
   - Finds similar content even when words don't match exactly
   - Works like finding books about similar topics, even if they use different words

Join us next time as we build the chat interface that will make all this information easily accessible to users!
# Part 5: Keeping Track of the Details with MongoDB

In our previous post, we set up vector search for scientific papers. Now, let's add support for storing and processing both scientific studies and articles that cite them. We'll use MongoDB to track metadata and manage relationships between sources.

## Understanding the Changes

Our upgraded system will:
- Process PDFs and web articles
- Extract and store text content in chunks
- Track citations between sources
- Enable metadata-based filtering

## Updated Data Models

First, we've enhanced our models to support different source types and citation tracking:

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

## Processing Sources

The `StudyService` class now includes methods for handling different source types:

```python
async def process_source(self, source: Source) -> List[Dict[str, Any]]:
    if source.url:
        text = await self._extract_text_from_url(source.url)
    elif source.pdf_path:
        text = await self._extract_text_from_pdf(source.pdf_path)
    else:
        raise ValueError("Source must have either URL or PDF path")
        
    chunks = self._chunk_text(text, chunk_size=512, overlap=50)
    return await self._process_chunks(chunks)
```

## Testing the Changes

1. Install additional dependencies:
```bash
pip install pymupdf beautifulsoup4 requests
```

2. Create a test script:

```python
import asyncio
from models import Source, SourceType, Author
from services import study_service
from datetime import datetime

async def test_source_processing():
    # Test with a PDF
    source = Source(
        type=SourceType.SCIENTIFIC_STUDY,
        pdf_path="path/to/study.pdf",
        title="Test Study",
        authors=[Author(name="Test Author")],
        publication_date=datetime.now()
    )
    
    chunks = await study_service.process_source(source)
    print(f"Generated {len(chunks)} chunks")
    
    # Test with a URL
    article_source = Source(
        type=SourceType.ARTICLE,
        url="https://example.com/article",
        title="Test Article",
        authors=[Author(name="Test Author")]
    )
    
    chunks = await study_service.process_source(article_source)
    print(f"Generated {len(chunks)} chunks")

if __name__ == "__main__":
    asyncio.run(test_source_processing())
```

3. Run the tests:
```bash
python -m pytest tests/
```

## Using the Enhanced Search

The search functionality now supports filtering by source type and metadata:

```python
from models import SearchQuery, SourceType

# Search only scientific studies
query = SearchQuery(
    query_text="AI in healthcare",
    source_type=SourceType.SCIENTIFIC_STUDY,
    min_citations=5,
    limit=10
)

results = await study_service.search_similar_studies(query)
```

## Next Steps

In Part 6, we'll build a chat interface that lets users:
- Ask questions about stored content
- Compare articles with their cited studies
- Get explanations of scientific concepts

Remember to update your MongoDB indexes for the new schema:

```javascript
db.studies.createIndex(
  { "source.text_chunks.vector": "vector" },
  { 
    name: "vector_index",
    vectorSearchOptions: {
      numDimensions: 768,
      similarity: "cosine"
    }
  }
)
```

The complete code is available in the repository. Next time, we'll turn this into an interactive chat system for debunking scientific misinformation!
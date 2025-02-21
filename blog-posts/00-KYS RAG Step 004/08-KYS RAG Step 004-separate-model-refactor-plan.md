# Refactoring Science Clickbait Decoder: Separating Studies and News Articles

## Current State

The Science Clickbait Decoder currently handles scientific studies and the articles that reference them in a single collection with vector embeddings for similarity search. While effective, this approach doesn't distinguish between primary sources (scientific studies) and secondary sources (news articles/blog posts). This makes it harder to verify claims and cross-reference information.

### Did you miss the earlier posts of this series?
Read Part 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0000). We tell the story about why we're building the tool.

Read Part 2 Step 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0001). Part 2 Step 1 is when the coding starts.

Read Step 2 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0002). In Step 2 we create the FastAPI, add HuggingFace's SciBERT Model, and connect the backend to FAISS.

Read Step 3 [HERE](https://i.til.show/python-fastapi-huggingface-faiss-science-clickbait-decoder-step-3). In Step 3 we add a MongoDB on Cloud Atlas to store data and setup a local MongoDB instance for back.

## Proposed Changes

### 1. Data Model Separation

#### Scientific Studies Model
```python
class ScientificStudy(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    title: str
    text: str
    authors: List[str]
    publication_date: datetime
    journal: str
    doi: Optional[str]
    topic: str
    discipline: str
    vector: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

#### News Articles Model
```python
class Article(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    title: str
    text: str
    author: str
    publication_date: datetime
    source_url: str
    publication_name: str
    related_scientific_studies: List[PyObjectId] = Field(default_factory=list)
    claims: List[Dict[str, str]] = Field(default_factory=list)
    topic: str
    vector: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### 2. Database Structure

- MongoDB Collections:
  - `scientific_studies`: Scientific papers and research
  - `articles`: News articles and blog posts
  - `claims`: Extracted claims from articles with verification status
  - `chat_history`: User conversations about scientific studies and articles

### 3. Service Layer Changes

#### ScientificStudyService
- CRUD operations for scientific studies
- Vector similarity search within scientific studies
- Metadata extraction and validation
- DOI verification and metadata fetching

#### Article Service
- CRUD operations for news articles
- Vector similarity search within articles
- Claim extraction and validation
- URL validation and metadata scraping
- Related scientific studies linking

#### Chat Service
- Separate chat contexts for scientific studies and articles
- Cross-referencing between articles and scientific studies
- Claim verification against scientific sources
- Citation and evidence tracking

### 4. API Endpoints

#### Scientific Studies API
```
GET /scientific-studies/ - List scientific studies with pagination
POST /scientific-studies/ - Create new scientific study
GET /scientific-studies/{id} - Get scientific study by ID
PUT /scientific-studies/{id} - Update scientific study
DELETE /scientific-studies/{id} - Delete scientific study
POST /scientific-studies/search - Vector similarity search
```

#### Articles API
```
GET /articles/ - List articles with pagination
POST /articles/ - Create new article
GET /articles/{id} - Get article by ID
PUT /articles/{id} - Update article
DELETE /articles/{id} - Delete article
POST /articles/search - Vector similarity search
GET /articles/{id}/scientific-studies - Get related scientific studies
POST /articles/{id}/claims - Add claims
GET /articles/{id}/claims - Get claims
```

#### Chat API
```
POST /chat/scientific-studies/{id} - Chat about scientific study
POST /chat/articles/{id} - Chat about article
GET /chat/history/{id} - Get chat history
POST /chat/verify - Verify article claims
```

### 5. Implementation Plan

1. **Phase 1: Model and Database Migration**
   - **Make sure you're in your virtual environment**
     - Install Requirements from `./requirements.txt`
     - `pip install -r requirements.txt`
     - We can install packages one at a time to identify and resolve conflicts if you get any errors:
      - `pip install package-name==specific.version`
   - Micgration Command `python -m app.core.db-migration`
   - Create new models for Article and Claims
   - Set up new MongoDB collections
   - Create database migration scripts
   - Update database manager for new collections
 - `Remember: A well-organized requirements.txt file is like a recipe - it helps others (or future yous) reproduce your development environment exactly. This is important when you're preparing to show your project to potential employers or clients.`

2. **Phase 2: Service Layer Implementation**
   - Implement ArticleService
   - Enhance ScientificStudyService
   - Create ClaimService
   - Develop ChatService

3. **Phase 3: API Development**
   - Create new API routes
   - Implement request/response handlers
   - Add validation and error handling
   - Update documentation

4. **Phase 4: Testing**
   - Unit tests for new models
   - Integration tests for services
   - API endpoint testing
   - End-to-end testing

### 6. Technical Considerations

#### Vector Search
- Maintain separate vector indices for scientific studies and articles
- Use same embedding model (SciBERT) for consistency
- Implement cross-collection search capabilities

#### Claim Verification
- Extract claims using NLP
- Link claims to specific text in scientific studies
- Calculate confidence scores for claim verification
- Track verification history

#### Performance
- Implement caching for frequently accessed items
- Use aggregation pipelines for efficient queries
- Optimize vector search with appropriate indices

### 7. Benefits

1. **Improved Accuracy**
   - Clear separation between primary and secondary sources
   - Better claim verification
   - Traceable citations

2. **Enhanced User Experience**
   - Targeted search within content types
   - Clear relationship between articles and scientific studies
   - Better context in chat interactions

3. **Maintainability**
   - Cleaner code organization
   - Easier to add new features
   - Better testing isolation

### 8. Future Enhancements

1. **Advanced Features**
   - Automated claim extraction
   - Citation network analysis
   - Bias detection in articles
   - Confidence scoring for claims

2. **Integration Possibilities**
   - Academic paper databases
   - News APIs
   - Fact-checking services
   - Citation managers

## Next Steps

1. Create GitHub issues for each phase
2. Set up project milestones
3. Begin with database schema updates
4. Create new model classes
5. Implement basic CRUD operations

This refactoring will significantly improve the Science Decoder's ability to help users verify scientific claims in news articles and blog posts while maintaining a clear separation between primary and secondary sources.

Stay tuned for more exciting features! If you need help, remember you can always:
- Check the MongoDB Atlas documentation
- Look at the FastAPI guides
- Ask questions in the MongoDB community forums
- Leave a comment telling me about your experience
- Reach out to me through the chat bubble at the bottom right corner of the screen

Did you miss the beginning of the Science Clickbait Decoder blog series?
Read Part 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0000). We tell the story about why we're building the tool.

Read Part 2 Step 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0001). Part 2 Step 1 is when the coding starts.

Read Step 2 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0002). In Step 2 we create the FastAPI, add HuggingFace's SciBERT Model, and connect the backend to FAISS.

Read Step 3 [HERE](https://i.til.show/python-fastapi-huggingface-faiss-science-clickbait-decoder-step-3). In Step 3 we add a MongoDB on Cloud Atlas to store data and setup a local MongoDB instance for back.

*Excited about what’s coming? Share your progress so far and stay tuned for what's next.*  

*If you have any questions or need help, feel free to ask.*
You may reach me by leaving a comment or clicking the chat bubble in the bottom right corner of the screen.

## Contact
For questions or inquiries, reach out at **a@awews.com**.
Chat with Brand Anthony McDonald in real-time by visiting
https://i.brandanthonymcdonald.com/portfolio
```
Text "CENT" to 833.752.8102 to join me on my journey to becoming the world's fastest centenarian.

Made with ❤️ by [BAM](https://i.brandanthonymcdonald.com/portfolio)
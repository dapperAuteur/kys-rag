# Refactoring Science Decoder: Separating Studies and News Articles

## Current State

The Science Decoder currently handles scientific studies in a single collection, with vector embeddings for similarity search. While effective, this approach doesn't distinguish between primary sources (scientific studies) and secondary sources (news articles/blog posts), making it harder to verify claims and cross-reference information.

## Proposed Changes

### 1. Data Model Separation

#### Scientific Studies Model
```python
class Study(BaseModel):
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
    related_studies: List[PyObjectId] = Field(default_factory=list)
    claims: List[Dict[str, str]] = Field(default_factory=list)
    topic: str
    vector: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### 2. Database Structure

- MongoDB Collections:
  - `studies`: Scientific papers and research
  - `articles`: News articles and blog posts
  - `claims`: Extracted claims from articles with verification status
  - `chat_history`: User conversations about studies and articles

### 3. Service Layer Changes

#### Study Service
- CRUD operations for scientific studies
- Vector similarity search within studies
- Metadata extraction and validation
- DOI verification and metadata fetching

#### Article Service
- CRUD operations for news articles
- Vector similarity search within articles
- Claim extraction and validation
- URL validation and metadata scraping
- Related studies linking

#### Chat Service
- Separate chat contexts for studies and articles
- Cross-referencing between articles and studies
- Claim verification against scientific sources
- Citation and evidence tracking

### 4. API Endpoints

#### Studies API
```
GET /studies/ - List studies with pagination
POST /studies/ - Create new study
GET /studies/{id} - Get study by ID
PUT /studies/{id} - Update study
DELETE /studies/{id} - Delete study
POST /studies/search - Vector similarity search
```

#### Articles API
```
GET /articles/ - List articles with pagination
POST /articles/ - Create new article
GET /articles/{id} - Get article by ID
PUT /articles/{id} - Update article
DELETE /articles/{id} - Delete article
POST /articles/search - Vector similarity search
GET /articles/{id}/studies - Get related studies
POST /articles/{id}/claims - Add claims
GET /articles/{id}/claims - Get claims
```

#### Chat API
```
POST /chat/studies/{id} - Chat about study
POST /chat/articles/{id} - Chat about article
GET /chat/history/{id} - Get chat history
POST /chat/verify - Verify article claims
```

### 5. Implementation Plan

1. **Phase 1: Model and Database Migration**
   - Create new models for Article and Claims
   - Set up new MongoDB collections
   - Create database migration scripts
   - Update database manager for new collections

2. **Phase 2: Service Layer Implementation**
   - Implement ArticleService
   - Enhance StudyService
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
- Maintain separate vector indices for studies and articles
- Use same embedding model (SciBERT) for consistency
- Implement cross-collection search capabilities

#### Claim Verification
- Extract claims using NLP
- Link claims to specific text in studies
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
   - Clear relationship between articles and studies
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
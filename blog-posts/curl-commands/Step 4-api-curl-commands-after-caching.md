# Science Decoder API Commands

## Health Check
```bash
curl -X GET http://localhost:8000/
```
```json
{
    "status": "ok",
    "message": "Welcome to the Science Decoder API!",
    "details": {
        "version": "2.0.0",
        "database_status": "healthy"
    }
}
```

## Scientific Studies

### Create Study
```bash
curl -X POST http://localhost:8000/scientific-studies/ \
-H "Content-Type: application/json" \
-d '{
    "title": "AI in Healthcare",
    "text": "Study about AI applications in healthcare",
    "authors": ["John Doe", "Jane Smith"],
    "publication_date": "2024-01-15T00:00:00Z",
    "journal": "Nature",
    "doi": "10.1234/example.doi",
    "topic": "AI Healthcare",
    "discipline": "Computer Science"
}'
```
```json
{
    "status": "success",
    "message": "Scientific study created successfully",
    "details": {
        "id": "65b123abc..."
    }
}
```

### Get Study
```bash
curl -X GET http://localhost:8000/scientific-studies/678185cfea562bee76945b97
```
```json
{
    "id": "678185cfea562bee76945b97",
    "title": "AI in Healthcare",
    "text": "Study about AI applications in healthcare",
    "authors": ["John Doe", "Jane Smith"],
    "publication_date": "2024-01-15T00:00:00Z",
    "journal": "Nature",
    "doi": "10.1234/example.doi",
    "topic": "AI Healthcare",
    "discipline": "Computer Science",
    "vector": [0.123, -0.456, ...],
    "created_at": "2024-01-24T10:00:00Z",
    "updated_at": "2024-01-24T10:00:00Z"
}
```
# NOT WORKING AS EXPECTED 
```
% curl -X PUT http://localhost:8000/scientific-studies/678185cfea562bee76945b97/citations \
-H "Content-Type: application/json" \
-d '["citation1", "citation2"]'
{"detail":"Scientific study not found"}%
```
### Update Study Citations
```bash
curl -X PUT http://localhost:8000/scientific-studies/678185cfea562bee76945b97/citations \
-H "Content-Type: application/json" \
-d '["citation1", "citation2"]'
```
```json
{
    "status": "success",
    "message": "Citations updated successfully",
    "details": {
        "id": "65b123abc"
    }
}
```

## Articles

### Create Article
```bash
curl -X POST http://localhost:8000/articles/ \
-H "Content-Type: application/json" \
-d '{
    "title": "New AI Healthcare Breakthrough",
    "text": "Article about recent AI developments in healthcare",
    "author": "John Writer",
    "publication_date": "2024-01-20T00:00:00Z",
    "source_url": "https://example.com/article",
    "publication_name": "Tech News",
    "topic": "AI Healthcare"
}'
```
```json
{
    "id": "6781866aea562bee76945b98",
    "title": "New AI Healthcare Breakthrough",
    "text": "Article about recent AI developments in healthcare",
    "author": "John Writer",
    "publication_date": "2024-01-20T00:00:00Z",
    "source_url": "https://example.com/article",
    "publication_name": "Tech News",
    "topic": "AI Healthcare",
    "created_at": "2024-01-24T10:00:00Z",
    "updated_at": "2024-01-24T10:00:00Z"
}
```

### Add Claim to Article
```bash
curl -X POST http://localhost:8000/articles/6781866aea562bee76945b98/claims \
-H "Content-Type: application/json" \
-d '{
    "text": "AI can diagnose cancer with 99% accuracy",
    "confidence_score": 0.8,
    "verified": false
}'
```
```json
{
    "status": "success",
    "message": "Claim added successfully",
    "details": {
        "article_id": "6781866aea562bee76945b98"
    }
}
```

### Verify Claim
```bash
curl -X PUT "http://localhost:8000/articles/6781866aea562bee76945b98/claims/0/verify?verification_notes=Found%20supporting%20evidence&confidence_score=0.9&verified=true"
```
```json
{
    "status": "success",
    "message": "Claim verification updated successfully",
    "details": {
        "article_id": "65b456def",
        "claim_index": 0
    }
}
```

### Link Study to Article
```bash
curl -X POST http://localhost:8000/articles/6781866aea562bee76945b98/scientific-studies/678185cfea562bee76945b97
```
```json
{
    "status": "success",
    "message": "Scientific study linked successfully",
    "details": {
        "article_id": "65b456def",
        "study_id": "65b123abc"
    }
}
```

## Search Operations

### Search All Content
```bash
curl -X POST http://localhost:8000/search/ \
-H "Content-Type: application/json" \
-d '{
    "query_text": "AI healthcare diagnosis",
    "limit": 5,
    "min_score": 0.5,
    "content_type": null
}'
```
```json
[
    {
        "content": {
            "id": "65b123abc",
            "title": "AI in Healthcare",
            "type": "scientific_study",
            ...
        },
        "score": 0.89,
        "content_type": "scientific_study"
    },
    {
        "content": {
            "id": "65b456def",
            "title": "New AI Healthcare Breakthrough",
            "type": "article",
            ...
        },
        "score": 0.78,
        "content_type": "article"
    }
]
```

# NOT WORKING AS EXPECTED 
```
 % curl -X GET "http://localhost:8000/search/topic/AI%20Healthcare?content_type=article&limit=2"
{"detail":"'ArticleService' object has no attribute 'search_by_topic'"}%
```
### Search by Topic
```bash
curl -X GET "http://localhost:8000/search/topic/AI%20Healthcare?content_type=article&limit=5"
```
```json
{
    "articles": [
        {
            "id": "65b456def",
            "title": "New AI Healthcare Breakthrough",
            ...
        }
    ]
}
```

### Find Related Content
```bash
curl -X GET "http://localhost:8000/search/related/article/6781866aea562bee76945b98?limit=5"
```
```json
{
    "articles": [...],
    "scientific_studies": [...]
}
```

## Chat Operations

### Save Chat Message
```bash
curl -X POST http://localhost:8000/chat/messages \
-H "Content-Type: application/json" \
-d '{
    "content_id": "678185cfea562bee76945b97",
    "content_type": "scientific_study",
    "message": "What are the main findings?",
    "user_id": "user123"
}'
```
```json
{
    "status": "success",
    "message_id": "65b789ghi",
    "timestamp": "2024-01-24T10:00:00Z"
}
```
# NOT WORKING AS EXPECTED 
```
Returned empty array instead of expected json.
```
### Get Chat History
```bash
curl -X GET "http://localhost:8000/chat/history/scientific_study/678185cfea562bee76945b97?limit=50"
```
```json
[
    {
        "content_id": "65b123abc",
        "content_type": "scientific_study",
        "message": "What are the main findings?",
        "timestamp": "2024-01-24T10:00:00Z",
        "user_id": "user123"
    }
]
```

# NOT WORKING AS EXCPECTED
```
% curl -X POST http://localhost:8000/chat/scientific-studies/678185cfea562bee76945b97 \
-H "Content-Type: application/json" \
-d '{
    "question": "What methodology was used in this study?"
}'
{"detail":"2 validation errors for ScientificStudyAnalysisResponse\nfindings\n  Field required [type=missing, input_value={'content_type': 'scienti...in Healthcare. Nature.'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.10/v/missing\nconfidence_score\n  Field required [type=missing, input_value={'content_type': 'scienti...in Healthcare. Nature.'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.10/v/missing"}%
```
### Analyze Scientific Study
```bash
curl -X POST http://localhost:8000/chat/scientific-studies/678185cfea562bee76945b97 \
-H "Content-Type: application/json" \
-d '{
    "question": "What methodology was used in this study?"
}'
```
```json
{
    "status": "success",
    "content_type": "scientific_study",
    "title": "AI in Healthcare",
    "findings": {
        "key_points": [...],
        "methodology": "...",
        "limitations": [...],
        "citation": "..."
    },
    "relevant_section": "...",
    "confidence_score": 0.85,
    "analysis_timestamp": "2024-01-24T10:00:00Z"
}
```
# NOT WORKING AS EXCPECTED
```
% curl -X POST http://localhost:8000/chat/articles/6781866aea562bee76945b98 \
-H "Content-Type: application/json" \
-d '{
    "question": "What claims does this article make about AI?"
}'
{"detail":"1 validation error for ArticleAnalysisResponse\nclaims.0.confidence_score\n  Field required [type=missing, input_value={'text': 'AI can diagnose...nd supporting evidence'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.10/v/missing"}%
```
### Analyze Article
```bash
curl -X POST http://localhost:8000/chat/articles/6781866aea562bee76945b98 \
-H "Content-Type: application/json" \
-d '{
    "question": "What claims does this article make about AI?"
}'
```
```json
{
    "status": "success",
    "content_type": "article",
    "title": "New AI Healthcare Breakthrough",
    "source": "Tech News",
    "publication_date": "2024-01-20T00:00:00Z",
    "claims": [...],
    "scientific_support": [...],
    "relevant_section": "...",
    "analysis_timestamp": "2024-01-24T10:00:00Z"
}
```

## Error Responses

### Not Found (404)
```json
{
    "detail": "Resource not found"
}
```

### Validation Error (422)
```json
{
    "detail": [
        {
            "loc": ["body", "title"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

### Server Error (500)
```json
{
    "detail": "Internal server error occurred"
}
```

## Testing Script
```bash
#!/bin/bash

# Test health check
echo "Testing health check..."
curl -s -X GET http://localhost:8000/

# Create scientific study
echo -e "\nCreating scientific study..."
STUDY_ID=$(curl -s -X POST http://localhost:8000/scientific-studies/ \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Test Study",
        "text": "Test content",
        "authors": ["Test Author"],
        "publication_date": "2024-01-24T00:00:00Z",
        "journal": "Test Journal",
        "topic": "Testing",
        "discipline": "Computer Science"
    }' | jq -r '.details.id')

# Create article
echo -e "\nCreating article..."
ARTICLE_ID=$(curl -s -X POST http://localhost:8000/articles/ \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Test Article",
        "text": "Test content",
        "author": "Test Author",
        "publication_date": "2024-01-24T00:00:00Z",
        "source_url": "https://example.com/test",
        "publication_name": "Test News",
        "topic": "Testing"
    }' | jq -r '.id')

# Link study to article
echo -e "\nLinking study to article..."
curl -s -X POST http://localhost:8000/articles/$ARTICLE_ID/scientific-studies/$STUDY_ID

# Add claim to article
echo -e "\nAdding claim to article..."
curl -s -X POST http://localhost:8000/articles/$ARTICLE_ID/claims \
    -H "Content-Type: application/json" \
    -d '{
        "text": "Test claim",
        "confidence_score": 0.8,
        "verified": false
    }'

# Search content
echo -e "\nSearching content..."
curl -s -X POST http://localhost:8000/search/ \
    -H "Content-Type: application/json" \
    -d '{
        "query_text": "test",
        "limit": 5,
        "min_score": 0.0
    }'

# Test chat functionality
echo -e "\nTesting chat..."
curl -s -X POST http://localhost:8000/chat/messages \
    -H "Content-Type: application/json" \
    -d "{
        \"content_id\": \"$STUDY_ID\",
        \"content_type\": \"scientific_study\",
        \"message\": \"What are the findings?\",
        \"user_id\": \"test_user\"
    }"
```
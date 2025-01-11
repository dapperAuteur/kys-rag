# Science Decoder API Commands


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
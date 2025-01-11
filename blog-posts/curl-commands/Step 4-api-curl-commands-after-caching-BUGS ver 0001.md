# Science Decoder API Commands

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
{"detail":"1 validation error for ScientificStudyAnalysisResponse\nfindings.key_points\n  Field required [type=missing, input_value={'key_findings': [], 'met...in Healthcare. Nature.'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.10/v/missing"}%
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
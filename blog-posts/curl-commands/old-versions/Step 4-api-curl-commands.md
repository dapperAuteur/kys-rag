# Science Decoder API Routes

## 1. Root Endpoint - Health Check
### Request:
```bash
curl -X GET http://localhost:8000/
```

### Expected Response:
```json
{
    "status": "ok",
    "message": "Welcome to the Science Decoder API!",
    "details": {
        "version": "2.0.0"
    }
}
```

## 2. Create Study
### Request:
```bash
curl -X POST http://localhost:8000/studies/ \
    -H "Content-Type: application/json" \
    -d '{
        "title": "AI in Healthcare",
        "text": "A comprehensive study about artificial intelligence applications in healthcare",
        "topic": "AI Healthcare",
        "discipline": "Computer Science"
    }'
```

### Expected Response:
```json
{
    "status": "success",
    "message": "Study created successfully",
    "details": {
        "id": "65b123abc..."  # MongoDB ObjectId
    }
}
```

## 3. Get Study by ID
### Request:
```bash
curl -X GET http://localhost:8000/studies/65b123abc...  # Replace with actual ID
```

### Expected Response:
```json
{
    "id": "65b123abc...",
    "title": "AI in Healthcare",
    "text": "A comprehensive study about artificial intelligence applications in healthcare",
    "topic": "AI Healthcare",
    "discipline": "Computer Science",
    "vector": [0.123, -0.456, ...]  # Vector embeddings
}
```

## 4. Search Similar Studies
### Request:
```bash
curl -X POST http://localhost:8000/search/ \
    -H "Content-Type: application/json" \
    -d '{
        "query_text": "artificial intelligence in medical diagnosis",
        "limit": 5,
        "min_score": 0.5
    }'
```

### Expected Response:
```json
[
    {
        "study": {
            "id": "65b123abc...",
            "title": "AI in Healthcare",
            "text": "A comprehensive study about artificial intelligence applications in healthcare",
            "topic": "AI Healthcare",
            "discipline": "Computer Science",
            "vector": [0.123, -0.456, ...]
        },
        "score": 0.89
    },
    {
        "study": {
            "id": "65b456def...",
            "title": "Machine Learning for Medical Imaging",
            "text": "Research on using ML for medical image analysis",
            "topic": "Medical AI",
            "discipline": "Computer Science",
            "vector": [0.789, -0.123, ...]
        },
        "score": 0.76
    }
]
```

## Error Response Examples

### 1. Not Found Error (404):
```json
{
    "detail": "Study not found"
}
```

### 2. Validation Error (422):
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

### 3. Server Error (500):
```json
{
    "detail": "Internal server error message"
}
```

## Testing with Environment Variables:
If you need to use different settings or environments:

```bash
# Set environment variable for testing
export MONGODB_ATLAS_URI="your_mongodb_uri"
export DATABASE_NAME="science_decoder"

# Or include in curl command
MONGODB_ATLAS_URI="your_mongodb_uri" curl -X GET http://localhost:8000/
```

## Batch Testing Script:
```bash
#!/bin/bash

# Test root endpoint
echo "Testing root endpoint..."
curl -X GET http://localhost:8000/

# Create a study
echo "\nCreating study..."
STUDY_ID=$(curl -X POST http://localhost:8000/studies/ \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Test Study",
        "text": "Test content",
        "topic": "Testing",
        "discipline": "Computer Science"
    }' | jq -r '.details.id')

# Get the created study
echo "\nGetting study..."
curl -X GET http://localhost:8000/studies/$STUDY_ID

# Search for similar studies
echo "\nSearching studies..."
curl -X POST http://localhost:8000/search/ \
    -H "Content-Type: application/json" \
    -d '{
        "query_text": "test search",
        "limit": 5,
        "min_score": 0.0
    }'
```
# Science Decoder API Guide: Working with curl

This guide shows you how to use curl commands to work with the Science Decoder API. Each section includes example commands and their expected responses. We'll explain what each command does in simple terms.

## Table of Contents
- [Checking API Status](#checking-api-status)
- [Working with Scientific Studies](#working-with-scientific-studies)
- [Working with Articles](#working-with-articles)
- [Search Operations](#search-operations)
- [Chat Features](#chat-features)

## Checking API Status

Let's start by making sure the API is working:

```bash
curl -X GET "http://localhost:8000/"
```

Expected Response:
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

This command checks if the API is running and if it can connect to the database. It's like checking if a website is working before you try to use it.

## Working with Scientific Studies

### Creating a New Scientific Study

```bash
curl -X POST "http://localhost:8000/scientific-studies/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Effects of Exercise on Brain Health",
    "text": "This study examines how regular exercise impacts cognitive function...",
    "authors": ["Jane Smith", "John Doe"],
    "publication_date": "2024-01-15T00:00:00Z",
    "journal": "Neuroscience Today",
    "topic": "Brain Health",
    "discipline": "Neuroscience"
  }'
```

Expected Response:
```json
{
    "status": "success",
    "message": "Scientific study created successfully",
    "details": {
        "id": "65abc123def456789"
    }
}
```

This command adds a new scientific study to the database. Think of it like submitting a book report to your teacher. The API gives you back a special ID number so you can find your study later.

### Getting a Scientific Study

```bash
curl -X GET http://localhost:8000/scientific-studies/65abc123def456789
```

Expected Response:
```json
{
    "title": "Effects of Exercise on Brain Health",
    "text": "This study examines how regular exercise impacts cognitive function...",
    "authors": ["Jane Smith", "John Doe"],
    "publication_date": "2024-01-15T00:00:00Z",
    "journal": "Neuroscience Today",
    "topic": "Brain Health",
    "discipline": "Neuroscience",
    "created_at": "2024-01-20T10:30:00Z",
    "updated_at": "2024-01-20T10:30:00Z"
}
```

This command retrieves a scientific study using its ID. It's like looking up a book in the library using its call number.

## Working with Articles

### Creating a New Article

Sample
```bash
curl -X POST "http://localhost:8000/articles/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Research Shows Exercise Boosts Brain Power",
    "text": "Scientists have discovered that regular exercise can improve memory...",
    "author": "Sarah Johnson",
    "publication_date": "2024-01-20T00:00:00Z",
    "source_url": "https://example.com/brain-exercise",
    "publication_name": "Health News Daily",
    "topic": "Brain Health"
  }'
```
Real Article
```bash
curl -X POST "https://archive.nytimes.com/well.blogs.nytimes.com/2016/04/27/1-minute-of-all-out-exercise-may-equal-45-minutes-of-moderate-exertion/?_r" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "1 Minute of All-Out Exercise May Have Benefits of 45 Minutes of Moderate Exertion",
    "text": "For many of us, the most pressing question about exercise is: How little can I get away with?...",
    "author": "Gretchen Reynolds",
    "publication_date": "2024-01-20T00:00:00Z",
    "source_url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0154075",
    "publication_name": "The New York Times",
    "topic": "Exercise"
  }'
```

Expected Response:
```json
{
    "status": "success",
    "message": "Article created successfully",
    "details": {
        "id": "65def789abc123456"
    }
}
```

This command adds a news article to the database. It's similar to adding a scientific study, but it includes different information like the website where the article was published.

### Linking a Scientific Study to an Article

```bash
curl -X POST "http://localhost:8000/articles/65def789abc123456/scientific-studies/65abc123def456789"
```

Expected Response:
```json
{
    "status": "success",
    "message": "Scientific study linked successfully",
    "details": {
        "article_id": "65def789abc123456",
        "study_id": "65abc123def456789"
    }
}
```

This command connects a news article to the scientific study it talks about. It's like drawing a line between two related pieces of information.

## Search Operations

### Searching All Content

```bash
curl -X POST "http://localhost:8000/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "exercise brain health",
    "limit": 5,
    "min_score": 0.5
  }'
```

Expected Response:
```json
[
    {
        "content": {
            "title": "Effects of Exercise on Brain Health",
            "text": "This study examines...",
            "content_type": "scientific_study",
            "score": 0.95
        }
    },
    {
        "content": {
            "title": "New Research Shows Exercise Boosts Brain Power",
            "text": "Scientists have discovered...",
            "content_type": "article",
            "score": 0.85
        }
    }
]
```

This command searches through both scientific studies and news articles to find information about exercise and brain health. It's like using a search engine that looks through both textbooks and newspaper articles at the same time.

## Chat Features

### Starting a Chat About a Scientific Study

```bash
curl -X POST "http://localhost:8000/chat/scientific-studies/65abc123def456789" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What were the main findings about exercise and memory?"
  }'
```

Expected Response:
```json
{
    "content_type": "scientific_study",
    "title": "Effects of Exercise on Brain Health",
    "key_findings": [
        "Regular exercise improved memory performance by 20%",
        "Participants who exercised showed better cognitive flexibility"
    ],
    "relevant_section": "The study demonstrated a significant improvement in memory tasks...",
    "methodology": "Researchers conducted a 6-month randomized controlled trial...",
    "limitations": ["Sample size was limited to 100 participants"]
}
```

This command lets you ask questions about a specific scientific study. It's like having a conversation with someone who has read and understood the study really well.

## Tips for Using These Commands

1. Replace "localhost:8000" with your actual API address if it's different.
2. Always use the correct ID numbers in your commands.
3. Make sure to include all required information when creating new items.
4. Check the response messages to make sure your commands worked correctly.

## Common Error Responses

When something goes wrong, you might see responses like this:

```json
{
    "detail": "Scientific study not found"
}
```
or
```json
{
    "detail": "Invalid input format"
}
```

These error messages help you understand what went wrong so you can fix the problem and try again.

## Need Help?

If you get stuck or need more information:
1. Check the API documentation
2. Make sure all your quotation marks and brackets match
3. Verify that your JSON data is properly formatted

Remember: You can use these commands to test the API, build applications, or create scripts to automate tasks.
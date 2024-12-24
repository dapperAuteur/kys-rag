# Part 5: Keeping Track of the Details with MongoDB

In our journey to build a scientific study search tool, we've reached an important milestone: storing and organizing our data effectively. Today, we'll add support for processing PDFs and article links, storing metadata, and preparing for our chat feature.

## Why MongoDB?

Think of MongoDB as a super-organized digital filing cabinet. It's perfect for our needs because:
1. It's free to start using
2. It works well with different types of data
3. It can store both text and special number patterns (vectors)
4. It's fast at searching through lots of information

## What We'll Build

By the end of this tutorial, you'll be able to:
- Upload PDFs of scientific studies
- Add links to articles that talk about scientific research
- Store all the important details about these documents
- Search through everything quickly
- Get ready for our upcoming chat feature

## Setting Up MongoDB

First, let's install MongoDB on your computer:

1. Download MongoDB Community Edition from mongodb.com
2. Install it following their instructions for your operating system
3. Create a database named `science_decoder`

For testing, we'll use a local MongoDB instance. Later, you can switch to MongoDB Atlas (their cloud service) for free hosting.

## Code Changes

We need to make several updates to our application. Let's go through them step by step.

### 1. New Dependencies

Add these to your `requirements.txt`:

```txt
pymongo==4.6.1
motor==3.3.2
python-multipart==0.0.9
pdfminer.six==20231228
beautifulsoup4==4.12.3
httpx==0.26.0
```

Install them with:
```bash
pip install -r requirements.txt
```

### 2. Configuration Updates

We'll update our configuration to include settings for document processing.

[See config.py artifact for the code]

### 3. Enhanced Models

Our data models need to support articles and their citations.

[See models.py artifact for the code]

### 4. Database Operations

We'll create specialized functions for handling documents and metadata.

[See database.py artifact for the code]

### 5. Document Processing Service

This new service will handle PDFs and web articles.

[See services.py artifact for the code]

### 6. API Updates

Finally, we'll add new endpoints for document uploads and processing.

[See main.py artifact for the code]

## Testing Our Changes

Let's test our new features:

1. Start your MongoDB server:
```bash
mongod
```

2. Run the application:
```bash
uvicorn main:app --reload
```

3. Try these test cases:

```python
import requests
import json

# Test uploading a PDF
with open('example.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload/pdf',
        files={'file': f}
    )
print(response.json())

# Test adding an article
article_data = {
    "url": "https://example.com/science-article",
    "title": "New AI Discovery",
    "cited_studies": [
        "https://doi.org/10.1234/example.123"
    ]
}
response = requests.post(
    'http://localhost:8000/articles/',
    json=article_data
)
print(response.json())
```

## What's Next?

In Part 6, we'll build an interactive chat feature that uses all this stored information to help users understand scientific studies and check if articles are reporting them accurately.

Some things to try before the next part:
1. Upload different types of PDFs and see how they're processed
2. Add articles with multiple cited studies
3. Try searching for studies using different topics and keywords
4. Experiment with the vector similarity search

Remember to keep your MongoDB running and regularly back up your data!

## Common Issues and Solutions

1. **MongoDB Connection Problems**
   - Make sure MongoDB is running (`mongod` command)
   - Check your connection string
   - Verify network access if using Atlas

2. **PDF Processing Errors**
   - Ensure PDFs are not password-protected
   - Check file permissions
   - Verify PDF is text-based (not scanned images)

3. **Vector Search Issues**
   - Confirm vector dimensions match
   - Check index creation success
   - Verify enough RAM for vector operations

Need help? Check the project's GitHub issues or start a discussion!
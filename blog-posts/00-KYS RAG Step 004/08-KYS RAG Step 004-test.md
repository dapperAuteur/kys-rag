# Testing Your Science Decoder API: A Complete Guide

When we build software, it's like building a house - we need to make sure every room works properly before moving in. In this guide, I'll show you how to test every part of our Science Decoder API, both automatically and manually. I'll explain what each test does in simple terms, so you can share this information with your team or clients.

## Setting Up Your Testing Environment

First, let's get everything ready to run our tests. Think of this like preparing your kitchen before cooking a big meal.

1. Make sure your application is running:
```bash
# Start your application
uvicorn main:app --reload
```

2. Open a new terminal window for running tests.

3. Install testing tools:
```bash
pip install pytest pytest-asyncio httpx
```

## Running Automated Tests

Our automated tests are like having a robot check every room in the house automatically. Here's how to run them:

```bash
# Run all tests with detailed output
pytest test_main.py -v

# Run tests and show print statements (useful for debugging)
pytest test_main.py -v -s
```

The tests will check:
- If the API starts correctly
- If we can create new studies
- If we can search for studies
- If we handle errors properly

## Manual Testing with cURL

Sometimes we want to check things ourselves, just like walking through each room of a house. Here's how to test each part of our API manually using cURL commands. I'll explain what each command does and what to expect.

### 1. Check if the API is Running
```bash
curl http://localhost:8000/
```
You should see a welcome message like:
```json
{
  "status": "ok",
  "message": "Welcome to the Science Decoder API!",
  "details": {"version": "2.0.0"}
}
```

### 2. Create a New Study
```bash
curl -X POST http://localhost:8000/studies/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Introduction to AI",
    "text": "Artificial Intelligence is transforming how we live and work.",
    "topic": "AI",
    "discipline": "Computer Science"
  }'
```
You should get back a success message with an ID:
```json
{
  "status": "success",
  "message": "Study created successfully",
  "details": {"id": "someIdHere"}
}
```
Save this ID - you'll need it for the next test!

### 3. Retrieve a Study
Replace `{study_id}` with the ID you got from creating the study:
```bash
curl http://localhost:8000/studies/{study_id}
```
You should see all the study details:
```json
{
  "title": "Introduction to AI",
  "text": "Artificial Intelligence is transforming how we live and work.",
  "topic": "AI",
  "discipline": "Computer Science",
  "created_at": "2024-12-23T..."
}
```

### 4. Search for Similar Studies
```bash
curl -X POST http://localhost:8000/search/ \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "artificial intelligence research",
    "limit": 5,
    "min_score": 0.0
  }'
```
You should get back a list of similar studies, ordered by how well they match your search:
```json
[
  {
    "study": {
      "title": "Introduction to AI",
      ...
    },
    "score": 0.95
  },
  ...
]
```

## Testing Different Scenarios

Just like we test a house under different conditions (rainy day, hot day, etc.), here are some special situations to test:

### Test Error Handling
Try to get a study that doesn't exist:
```bash
curl http://localhost:8000/studies/nonexistentid
```
You should get a proper error message:
```json
{
  "detail": "Study not found"
}
```

### Test Search with Various Queries
Try searching with different types of text:
```bash
curl -X POST http://localhost:8000/search/ \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "biology research methods",
    "limit": 3,
    "min_score": 0.5
  }'
```

## Common Issues and Solutions

Sometimes things don't work as expected. Here are common problems and how to fix them:

1. **Connection Refused Error**
   - Make sure your application is running
   - Check if the port 8000 is free
   - Try restarting the application

2. **Database Errors**
   - Verify your MongoDB connection string
   - Check if MongoDB is running
   - Look at the application logs for detailed error messages

3. **Empty Search Results**
   - Add more studies to the database
   - Try broader search terms
   - Reduce the min_score value

## Monitoring Test Results

When running tests, pay attention to:
1. Response times - how quickly does the API respond?
2. Error messages - are they clear and helpful?
3. Data consistency - does the returned data match what you sent?

## Next Steps

After testing, you might want to:
1. Set up automated testing in your deployment pipeline
2. Add more test cases for specific business requirements
3. Create a monitoring system for production use

## For Business Stakeholders

When reviewing this API with business stakeholders, emphasize:
1. The API's reliability through comprehensive testing
2. Clear error handling for better user experience
3. Flexibility in searching and retrieving scientific content
4. Scalability for growing content collections

Remember, good testing helps ensure your application works reliably and helps catch problems before they affect your users. It's like having a quality control team checking every part of your house before someone moves in.

Would you like me to explain any part of these tests in more detail?
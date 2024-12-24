Create a .env file with your MongoDB Atlas credentials:
MONGODB_ATLAS_URI=mongodb+srv://<your_username>:<your_password>@<your_cluster>.mongodb.net/

Test saving a study:

curl -X POST "http://127.0.0.1:8000/save-study" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Climate Change Effects",
    "text": "Global temperatures are rising due to human activities.",
    "topic": "Environment",
    "discipline": "Climate Science"
  }'

curl -X POST "http://127.0.0.1:8000/save-study" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Study",
    "text": "This is a test study about renewable energy and its impact on climate change.",
    "topic": "renewable energy",
    "discipline": "environmental science"
}'

Retrieve studies:
curl "http://127.0.0.1:8000/get-studies/Environment"

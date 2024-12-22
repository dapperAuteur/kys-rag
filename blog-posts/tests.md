Create a .env file with your MongoDB Atlas credentials:
MONGODB_ATLAS_URI=mongodb+srv://<your_username>:<your_password>@<your_cluster>.mongodb.net/

Test saving a study:

curl -X POST "http://127.0.0.1:8000/save-study" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Climate Change Effects",
    "text": "Global temperatures are rising...",
    "topic": "Environment",
    "discipline": "Climate Science"
  }'


Retrieve studies:
curl "http://127.0.0.1:8000/get-studies/Environment"

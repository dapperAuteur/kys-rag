### **Step 3: Storing Data with MongoDB for Smarter Science Decoding**  

Welcome back! In Step 2, we built the **brain** of the Science Decoder Tool. With FastAPI, Hugging Face SciBERT, and FAISS, your tool can now process questions, understand scientific text, and perform lightning-fast searches. You even tested your backend with Curl and saw it in action.  

Now it’s time to give your tool some memory. In Step 3, we’ll set up a **database using MongoDB** to store scientific studies, organize them by topics and disciplines, and make the data easily retrievable. By the end of this step, your tool will be ready to persist data, making it more reliable and powerful.  

---

### **What We’ll Do in Step 3**
Here’s what’s on the menu:  
1. **Set Up MongoDB**: Install and connect to MongoDB for persistent data storage.  
2. **Design a Schema**: Organize metadata for studies to make them searchable.  
3. **Store and Retrieve Data**: Add functions to save and fetch studies from the database.  
4. **Test Everything**: Use Curl to verify the tool stores and retrieves data correctly.  

---

### **Why This Step Matters**  
Without a database, your tool can only handle data while it’s running. As soon as you shut it down, everything is lost. MongoDB solves this problem by acting as the memory for your tool. It keeps studies and metadata safe and makes them easy to search and update later.  

---

### **Step-by-Step Guide to Setting Up MongoDB**

#### **Step 3.1: Install and Run MongoDB**  
1. **Install MongoDB Community Edition**:  
   - Visit [MongoDB Download Center](https://www.mongodb.com/try/download/community) and download the version for your operating system.  

2. **Start MongoDB**:  
   - Once installed, open your terminal and start the MongoDB service:  
     ```bash
     mongod
     ```  
   - MongoDB will now run locally on `localhost:27017`.  

3. **Install the MongoDB Python Driver**:  
   - Use the following command to install `pymongo`:  
     ```bash
     pip install pymongo
     ```  

---

#### **Step 3.2: Design a Schema for Studies**  
In `main.py`, define a function to organize how studies are stored in MongoDB:  
1. Import the MongoDB client:  
   ```python
   from pymongo import MongoClient
   ```  

2. Connect to MongoDB and create a database:  
   ```python
   client = MongoClient("mongodb://localhost:27017/")
   db = client["science_decoder"]
   studies_collection = db["studies"]
   ```  

3. Add a function to save studies:  
   ```python
   class Study(BaseModel):
       title: str
       text: str
       topic: str
       discipline: str

   @app.post("/save-study")
   def save_study(study: Study):
       study_data = {
           "title": study.title,
           "text": study.text,
           "topic": study.topic,
           "discipline": study.discipline
       }
       result = studies_collection.insert_one(study_data)
       return {"message": "Study saved", "id": str(result.inserted_id)}
   ```  

4. Add a function to retrieve studies by topic:  
   ```python
   @app.get("/get-studies/{topic}")
   def get_studies_by_topic(topic: str):
       studies = list(studies_collection.find({"topic": topic}))
       for study in studies:
           study["_id"] = str(study["_id"])  # Convert ObjectId to string
       return {"studies": studies}
   ```  

---

#### **Step 3.3: Test the Database**  
1. **Save a Study**: Use Curl to save a study:  
   ```bash
   curl -X POST "http://127.0.0.1:8000/save-study" -H "Content-Type: application/json" -d '{
     "title": "The Effects of Climate Change",
     "text": "This study discusses the impact of rising temperatures on ecosystems.",
     "topic": "Environment",
     "discipline": "Ecology"
   }'
   ```  
   - You should see a response like this:  
     ```json
     {"message": "Study saved", "id": "64c8c5d0d293f8231a5e0a9c"}
     ```  

2. **Retrieve Studies by Topic**: Use Curl to fetch all studies under a topic:  
   ```bash
   curl -X GET "http://127.0.0.1:8000/get-studies/Environment"
   ```  
   - The response should include the study you just saved:  
     ```json
     {"studies":[{"_id":"64c8c5d0d293f8231a5e0a9c","title":"The Effects of Climate Change","text":"This study discusses the impact of rising temperatures on ecosystems.","topic":"Environment","discipline":"Ecology"}]}
     ```  

---

### **Strengths of This Approach**  
- **Persistence**: Data is stored permanently and won’t disappear when the server restarts.  
- **Scalability**: MongoDB can handle large datasets with ease.  
- **Organization**: Structuring metadata makes searching studies by topic or discipline simple.  

### **Weaknesses to Watch Out For**  
- **Setup Complexity**: Setting up MongoDB may feel overwhelming if you’re new to databases.  
- **Testing Time**: Testing every endpoint with Curl takes patience but ensures everything works.  

---

### **Celebrate Your Progress!**  
You’ve just taught your tool to remember! It can now save studies, organize them by topic and discipline, and fetch them later for analysis. You’re no longer limited to temporary data.  

---

### **What’s Next?**  
In **Step 4**, we’ll combine MongoDB with FAISS to make searching even smarter. By storing embeddings alongside metadata, your tool will be able to retrieve both relevant text and key details in one seamless step.  

Stay tuned, and let’s keep building!  
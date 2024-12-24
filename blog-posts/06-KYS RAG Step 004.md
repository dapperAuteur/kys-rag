### **Step 4: Combining MongoDB and FAISS for Smarter Science Searches**  

Welcome back! In Step 3, we gave our Science Decoder Tool a memory by adding MongoDB. Now, your tool can save scientific studies, organize them by topic and discipline, and fetch them later for analysis. Great job!  

In Step 4, we’ll take things to the next level by combining MongoDB and FAISS. This will allow your tool to search both the metadata (e.g., topics, disciplines) and the text embeddings (meaningful representations of study content). By the end of this step, your tool will be smarter, faster, and ready to tackle complex questions more efficiently.  

---

### **What We’ll Do in Step 4**  
Here’s what’s on the menu today:  
1. **Store Embeddings in MongoDB**: Save the FAISS vector embeddings alongside metadata in MongoDB.  
2. **Integrate FAISS with MongoDB**: Rebuild the FAISS index on startup using stored embeddings.  
3. **Perform Combined Searches**: Fetch relevant studies based on both metadata and embedding similarity.  
4. **Test Everything**: Use Curl to verify combined searches are working.  

---

### **Why This Step Matters**  
This integration makes your tool even more powerful by combining **speed** (FAISS) with **organization** (MongoDB). Now, you can:  
- Search for studies by topic or discipline.  
- Find studies with similar content, even if the metadata doesn’t match exactly.  

---

### **Step-by-Step Guide to Combining MongoDB and FAISS**

#### **Step 4.1: Update Your Schema to Include Embeddings**  
In Step 3, we stored metadata in MongoDB. Now, let’s update the schema to also include text embeddings.  

1. Modify the `Study` class in `main.py`:  
   ```python
   class Study(BaseModel):
       title: str
       text: str
       topic: str
       discipline: str
       embedding: list  # Add embeddings
   ```  

2. Update the `/save-study` endpoint to generate and save embeddings:  
   ```python
   @app.post("/save-study")
   def save_study(study: Study):
       # Generate embedding for the study text
       inputs = tokenizer(study.text, return_tensors="pt", truncation=True, max_length=512)
       with torch.no_grad():
           embedding = model(**inputs).last_hidden_state.mean(dim=1).squeeze().tolist()
       
       study_data = {
           "title": study.title,
           "text": study.text,
           "topic": study.topic,
           "discipline": study.discipline,
           "embedding": embedding
       }
       result = studies_collection.insert_one(study_data)
       return {"message": "Study saved", "id": str(result.inserted_id)}
   ```  

---

#### **Step 4.2: Rebuild FAISS Index on Startup**  
When the app starts, load all embeddings from MongoDB and rebuild the FAISS index.  

1. Update the FAISS index initialization in `main.py`:  
   ```python
   # Initialize FAISS index
   index = faiss.IndexFlatL2(768)

   # Load existing embeddings from MongoDB
   existing_studies = studies_collection.find()
   embeddings = []
   for study in existing_studies:
       if "embedding" in study:
           embeddings.append(study["embedding"])
   
   if embeddings:
       index.add(np.array(embeddings, dtype="float32"))
   ```  

---

#### **Step 4.3: Perform Combined Searches**  
Add an endpoint to search for studies based on embedding similarity.  

1. Create a `/search-studies` endpoint:  
   ```python
   @app.post("/search-studies")
   def search_studies(query_text: str):
       # Generate embedding for the query
       inputs = tokenizer(query_text, return_tensors="pt", truncation=True, max_length=512)
       with torch.no_grad():
           query_embedding = model(**inputs).last_hidden_state.mean(dim=1).squeeze().numpy()
       
       # Search FAISS for similar embeddings
       distances, indices = index.search(np.array([query_embedding], dtype="float32"), k=5)
       
       # Fetch studies from MongoDB using the indices
       results = []
       for idx in indices[0]:
           if idx < studies_collection.count_documents({}):
               results.append(studies_collection.find_one({}, skip=idx))
       
       # Convert ObjectIds to strings
       for result in results:
           result["_id"] = str(result["_id"])
       
       return {"results": results}
   ```  

---

#### **Step 4.4: Test the Integration**  
1. **Save a Study**: Use Curl to save a study with an embedding:  
   ```bash
   curl -X POST "http://127.0.0.1:8000/save-study" -H "Content-Type: application/json" -d '{
     "title": "The Impact of Renewable Energy",
     "text": "This study explores the benefits of wind and solar energy.",
     "topic": "Energy",
     "discipline": "Engineering"
   }'
   ```  

2. **Search for Similar Studies**: Use Curl to perform a combined search:  
   ```bash
   curl -X POST "http://127.0.0.1:8000/search-studies" -H "Content-Type: application/json" -d '{
     "query_text": "What are the benefits of solar energy?"
   }'
   ```  
   - You’ll see a list of studies with similar content:  
     ```json
     {"results":[{"_id":"64c9a89f3e0a5f001c9ec9a3","title":"The Impact of Renewable Energy","text":"This study explores the benefits of wind and solar energy.","topic":"Energy","discipline":"Engineering"}]}
     ```  

---

### **Final Version of `main.py` After Step 4**
The full, updated `main.py` file is . You can use it to run the entire project so far.  

---

### **Strengths of This Approach**  
- **Versatility**: Combines metadata and content-based searches for maximum flexibility.  
- **Scalability**: MongoDB handles large datasets, while FAISS ensures fast queries.  
- **Accuracy**: Embedding-based searches improve results for vague or imprecise queries.  

### **Weaknesses to Watch Out For**  
- **Reindexing Overhead**: Adding many new studies may require reloading the FAISS index.  
- **Complex Queries**: Advanced queries may need additional optimization in MongoDB.  

---

### **Celebrate Your Progress!**  
You’ve built a smarter Science Decoder Tool that combines the speed of FAISS with the persistence of MongoDB. Now, it can search for relevant studies with precision and reliability.  

---

### **What’s Next?**  
In **Step 5**, we’ll create an interactive chat interface using Next.js. Users will be able to ask questions, view study results, and explore information visually—all from a sleek, responsive frontend.  

Stay tuned, and let’s keep building!  
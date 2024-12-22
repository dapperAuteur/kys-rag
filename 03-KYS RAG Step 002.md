### **Step 2: Building the Brain of the Science Decoder Tool**  

Welcome back! In Step 1, we laid the foundation for the Science Decoder Tool. You set up your computer with Python, installed Visual Studio Code, and gathered the libraries needed to handle scientific data and create our tool. That was the groundwork. Now it’s time to build the **brain**—the part that processes questions, retrieves information, and generates helpful answers.  

This step is where we turn an idea into something you can interact with. By the end of this post, you’ll have a working backend that can answer questions, retrieve data, and even show off its skills to friends, hiring managers, or anyone curious.  

---

### **What We’ll Do in Step 2**  
Here’s what’s on the menu today:  
1. Create the backend using FastAPI, a fast and easy-to-use tool for building APIs.  
2. Add Hugging Face’s SciBERT, an AI model trained to understand scientific language.  
3. Use FAISS to make searching for data lightning-fast.  
4. Test everything to make sure it works.  

---

### **Why This Step Matters**  
The backend is the engine of our Science Decoder Tool. It handles user questions, finds relevant data, and prepares clear, accurate answers. Think of it like a chef in a restaurant—you give an order, and the chef (the backend) makes sure you get exactly what you asked for.  

---

### **Step-by-Step Guide to Building the Backend**  

#### **Step 2.1: Create Your Backend Project**  
Start by setting up your project folder and creating a Python virtual environment:  
1. Open Visual Studio Code.  
2. In the terminal, create a folder and navigate to it:  
   ```bash
   mkdir science-decoder
   cd science-decoder
   ```  

3. Create a virtual environment:  
   ```bash
   python -m venv env
   source env/bin/activate  # Use "env\Scripts\activate" on Windows
   ```  

4. Create a file called `main.py`. This will be the starting point for your backend.  

---

#### **Step 2.2: Set Up FastAPI**  
1. Install FastAPI and Uvicorn:  
   ```bash
   pip install fastapi uvicorn
   ```  

2. Add this code to `main.py` to start your API:  
   ```python
   from fastapi import FastAPI

   app = FastAPI()

   @app.get("/")
   def read_root():
       return {"message": "Welcome to the Science Decoder Tool!"}
   ```  

3. Run the app:  
   ```bash
   uvicorn main:app --reload
   ```  
   Visit `http://127.0.0.1:8000` in your browser, and you’ll see:  
   ```json
   {"message": "Welcome to the Science Decoder Tool!"}
   ```  

---

#### **Step 2.3: Add Hugging Face SciBERT**  
1. Install Hugging Face Transformers:  
   ```bash
   pip install transformers
   ```  

2. Add the SciBERT model to `main.py`:  
   ```python
   from transformers import AutoTokenizer, AutoModelForQuestionAnswering

   tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
   model = AutoModelForQuestionAnswering.from_pretrained("allenai/scibert_scivocab_uncased")

   @app.post("/ask")
   def answer_question(question: str, context: str):
       inputs = tokenizer(question, context, return_tensors="pt")
       outputs = model(**inputs)
       answer_start = outputs.start_logits.argmax()
       answer_end = outputs.end_logits.argmax() + 1
       answer = tokenizer.convert_tokens_to_string(
           tokenizer.convert_ids_to_tokens(inputs.input_ids[0][answer_start:answer_end])
       )
       return {"answer": answer}
   ```  

3. Test it:  
   - Save this example text to a file called `example_context.txt`:  
     ```
     The Earth revolves around the Sun and takes approximately 365.25 days to complete one orbit.
     ```  

   - Use Curl to ask a question:  
     ```bash
     curl -X POST "http://127.0.0.1:8000/ask" -H "Content-Type: application/json" -d '{"question":"How long does the Earth take to orbit the Sun?", "context":"The Earth revolves around the Sun and takes approximately 365.25 days to complete one orbit."}'
     ```  
   - You should see an answer like this:  
     ```json
     {"answer":"365.25 days"}
     ```  
   - Share your success with a friend or on social media!  

---

#### **Step 2.4: Add FAISS for Fast Search**  
1. Install FAISS:  
   ```bash
   pip install faiss-cpu
   ```  

2. Add this code to index and search vectors:  
   ```python
   import faiss
   import numpy as np

   index = faiss.IndexFlatL2(768)

   # Example: Add random data to the index
   data = np.random.random((10, 768)).astype("float32")
   index.add(data)

   @app.get("/search")
   def search_vectors(query_vector: list):
       query = np.array([query_vector]).astype("float32")
       distances, indices = index.search(query, k=5)
       return {"distances": distances.tolist(), "indices": indices.tolist()}
   ```  

3. Test it:  
   - Add this test query to `main.py`:  
     ```python
     import random

     @app.get("/test-search")
     def test_search():
         query_vector = np.random.random(768).astype("float32")
         distances, indices = index.search(np.array([query_vector]), k=3)
         return {"query": query_vector.tolist(), "distances": distances.tolist(), "indices": indices.tolist()}
     ```  

   - Use Curl to test it:  
     ```bash
     curl -X GET "http://127.0.0.1:8000/test-search"
     ```  
   - You’ll see something like this:  
     ```json
     {"query":[...],"distances":[[0.123,...]],"indices":[[0,1,2]]}
     ```  

---

### **Celebrate Your Progress!**  
You’ve built the brain of the Science Decoder Tool! It can now:  
- Answer scientific questions using Hugging Face’s SciBERT.  
- Search data efficiently with FAISS.  

---

### **What’s Next?**  
In **Step 3**, we’ll set up a database using MongoDB to store scientific studies, organize them by topic and discipline, and make them easy to retrieve. We’ll also link the database to FAISS for smarter search capabilities.  

Stay tuned, and keep building!  
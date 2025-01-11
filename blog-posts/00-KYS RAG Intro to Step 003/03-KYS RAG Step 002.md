### **Step 2: Building the Brain of the Science Decoder Tool**  

Welcome back! If you’ve followed along from Step 1, congratulations—you’ve already set up the foundation for our project. You’ve installed Python, Visual Studio Code, and the libraries we’ll use to process scientific studies and power our Retrieval-Augmented Generation (RAG) tool. Now, it’s time to bring our tool to life by building its **brain**—the backend.  

Did you miss the beginning of the Science Clickbait Decoder blog series?
Read Part 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0000).
Read Part 2 Step 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0001). Part 2 Step 1 is when the coding starts.

In this step, we’ll focus on creating the part of the tool that processes questions, retrieves information, and prepares the answers. This is where the magic happens, and by the end of this post, you’ll have a basic working backend to show off!  

---

### **What We’ll Do in Step 2**  
Here’s what’s on the agenda today:  
1. **Create a Backend with FastAPI**: This lightweight framework will serve as the brain of our tool.  
2. **Integrate Hugging Face’s SciBERT Model**: This pre-trained AI will help us summarize and explain scientific studies.  
3. **Connect the Backend to FAISS**: This will make retrieving the right chunks of data fast and efficient.  

---

### **Why This Step Matters**  
Think of the backend as the command center for your tool. It processes user requests, finds the most relevant data, and returns clear, accurate answers. Without it, our tool is just an idea with no way to function.  

---

### **Step-by-Step Guide to Building the Backend**  

#### **Step 2.1: Create a New Python Project**  
1. Open Visual Studio Code.  
2. In the terminal, create a new folder for your project and navigate to it:  
   ```bash
   mkdir science-decoder
   cd science-decoder
   ```  

3. Create a Python virtual environment (this keeps your libraries organized):  
   ```bash
   python -m venv env
   source env/bin/activate  # Use "env\Scripts\activate" on Windows
   ```  

4. Open a new file called `main.py` inside the folder. This will be your backend's starting point.  

---

#### **Step 2.2: Set Up FastAPI**  
1. In `main.py`, write the following code to start your FastAPI app:  
   ```python
   from fastapi import FastAPI

   app = FastAPI()

   @app.get("/")
   def read_root():
       return {"message": "Welcome to the Science Decoder Tool!"}
   ```  

2. Run your FastAPI app:  
   ```bash
   uvicorn main:app --reload
   ```  
   - Open your browser and go to `http://127.0.0.1:8000`. You should see:  
     ```json
     {"message": "Welcome to the Science Decoder Tool!"}
     ```  
   - Celebrate! You’ve built a working backend.  

---

#### **Step 2.3: Integrate Hugging Face’s SciBERT Model**  
SciBERT helps us make sense of scientific language. Let’s set it up:  
1. Install the Hugging Face Transformers library (if you haven’t already):  
   ```bash
   pip install transformers
   ```  

2. Add the SciBERT model to your `main.py`:  
   ```python
   from transformers import AutoTokenizer, AutoModelForQuestionAnswering

   tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
   model = AutoModelForQuestionAnswering.from_pretrained("allenai/scibert_scivocab_uncased")
   ```  

3. Test it by creating a function that answers simple questions:  
   ```python
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

   Now, send a question to your app using a tool like Postman or Curl and see it work!

4. Test it:  
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

#### **Step 2.4: Connect to FAISS**  
FAISS is the tool that quickly finds relevant chunks of data. Let’s integrate it:  
1. Install FAISS if you haven’t already:  
   ```bash
   pip install faiss-cpu
   ```  

2. Add a simple FAISS search function:  
   ```python
   import faiss
   import numpy as np

   index = faiss.IndexFlatL2(768)  # 768 matches the vector size of SciBERT

   # Example data to index
   data = np.random.random((10, 768)).astype("float32")
   index.add(data)

   @app.get("/search")
   def search_vectors(query_vector: list):
       query = np.array([query_vector]).astype("float32")
       distances, indices = index.search(query, k=5)
       return {"distances": distances.tolist(), "indices": indices.tolist()}
   ```  

   Test this by adding some vectors and searching for the closest match. 

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

### **Strengths of This Approach**  
- **Simplicity**: FastAPI makes it easy to build and test APIs.  
- **Speed**: FAISS ensures quick data retrieval.  
- **Accuracy**: Hugging Face’s SciBERT is trained specifically for scientific text.  

### **Weaknesses to Watch Out For**  
- **Limited Context**: SciBERT processes one question at a time, so it doesn’t “remember” past questions. We’ll address this in Step 3.  
- **Learning Curve**: New tools like FAISS might feel tricky at first, but practice makes perfect.  

---

### **Celebrate Your Progress!**  
You’ve just built the brain of the Science Decoder Tool! You now have a backend that can:  
- Answer questions using SciBERT.  
- Quickly search through indexed data with FAISS.  

---

### **What’s Next?**  
In **Step 3**, we’ll tackle the database. You’ll learn to use MongoDB to store and manage the data for your tool. Plus, we’ll connect MongoDB to our FAISS index to make the tool even more powerful.  

Get ready to take your project to the next level. See you in the next post!  

---

*Excited about what’s coming? Share your progress so far and stay tuned for Step 3.*  

*If you have any questions or need help, feel free to ask.*
You may reach me by leaving a comment or clicking the chat bubble in the bottom right corner of the screen.

Did you miss the beginning of the Science Clickbait Decoder blog series?
Read Part 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0000).
Read Part 2 Step 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0001). Part 2 Step 1 is when the coding starts.
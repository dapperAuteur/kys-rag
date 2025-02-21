### **Step 2: Building the Brain of the Science Decoder Tool**  

Welcome back! Congratulations to everyone that's followed along from Step 1. We’ve set up the foundation for our project.
What's included in the foundation:
- You’ve installed:
  - Python,
  - Visual Studio Code,
  - and the libraries we’ll use to process scientific studies and power our Retrieval-Augmented Generation (RAG) tool.
  
Now, we build the **brain**, (server,api and backend), to bring the Science Decoder tool to life.  

Did you miss the beginning of the Science Clickbait Decoder blog series?
Read Part 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0000). Part 1 is where talk about what we're going to do.
Read Part 2 Step 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0001). Part 2 Step 1 is when the coding starts.

Today we’ll focus on developing the brain. The brain processes questions, retrieves information, and prepares the answers. This is where the magic happens. We’ll have a basic working backend to show off by the end of this post.  

---

### **What We’ll Do in Step 2**  
Today's Agenda:  
1. **Create a Backend with FastAPI**: FastAPI is a lightweight framework that will serve as the brain of our tool.  
2. **Integrate Hugging Face’s SciBERT Model**: Hugging Face's SciBERT Model is a pre-trained AI. It'll help us summarize and explain scientific studies.  
3. **Connect the Backend to FAISS**: Connecting the backend to FAISS will make retrieving the right chunks of data fast and efficient.  

---

### **Why This Step Matters**  
Think of the backend as the command center and **brains** for our tool. It processes user requests and finds the most relevant data. Then, it returns clear and accurate answers, hopefully. It's a computer and is only as good as the instructions it's given. Our tool is just an idea with no way to function without the **brains**.  

---

### **Step-by-Step Guide to Building the Backend**  

#### **Step 2.1: Create a New Python Project**  
1. Open Visual Studio Code.  
2. In the terminal, create a new folder for our project and navigate to it:  
   ```bash
   mkdir science-decoder
   cd science-decoder
   ```  

3. Create a Python virtual environment (this keeps our libraries organized):  
   ```bash
   python -m venv env
   source env/bin/activate  # Use "env\Scripts\activate" on Windows
   ```  

4. Open a new file called `main.py` inside the folder. This will be our backend's starting point.  

---

#### **Step 2.2: Set Up FastAPI**  
1. In `main.py`, write the following code to start our FastAPI app:  
   ```python
   from fastapi import FastAPI

   app = FastAPI()

   @app.get("/")
   def read_root():
       return {"message": "Welcome to the Science Decoder Tool!"}
   ```  

2. Run our FastAPI app:  
   ```bash
   uvicorn main:app --reload
   ```  
   - Open our browser and go to `http://127.0.0.1:8000`. We should see:  
     ```json
     {"message": "Welcome to the Science Decoder Tool!"}
     ```  
   - Celebrate! We’ve built a working backend.  

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

---

#### **Step 2.4: Connect to FAISS**  
FAISS is the tool that quickly finds relevant chunks of data. FAISS stands for Facebook AI Similarity Search. It's a library that allows developers to quickly search for embeddings of multimedia documents that are similar to each other. It includes nearest-neighbor search implementations. Let’s integrate it:  
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

---

### **Strengths of This Approach**  
- **Simplicity**: FastAPI makes it easy to build and test APIs.  
- **Speed**: FAISS ensures quick data retrieval.  
- **Accuracy**: Hugging Face’s SciBERT is trained specifically for scientific text.  

### **Weaknesses to Watch Out For**  
- **Limited Context**: SciBERT processes one question at a time, so it doesn’t “remember” past questions. We’ll address this in Step 3.  
- **Learning Curve**: It takes time to learn new tools like FAISS. It might feel challenging at first. That means we're learning. Don't give up.  

---

### **Celebrate Our Progress!**  
We built the brain of the Science Decoder Tool! Now we have a backend that can:  
- Answer questions using SciBERT.  
- Quickly search through indexed data with FAISS.  

---

### **What’s Next?**  
In **Step 3**, we’ll tackle the database. You’ll learn to use MongoDB to store and manage the data for our tool. Plus, we’ll connect MongoDB to our FAISS index to make the tool even more powerful.  

Get ready to take your project to the next level. See you in the next post!  

---

*Excited about what’s coming? Share your progress so far and stay tuned for Step 3.*  

*If you have any questions or need help, feel free to ask.*
You may reach me by leaving a comment or clicking the chat bubble in the bottom right corner of the screen.

Did you miss the beginning of the Science Clickbait Decoder blog series?
Read Part 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0000).
Read Part 2 Step 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0001). Part 2 Step 1 is when the coding starts.
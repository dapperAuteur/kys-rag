### **Step 3: Adding Memory to Your Science Decoder Tool**

#### [**Quick Recap of Step 2**](https://i.til.show/decoding-clickbait-science-articles-with-ai-0002)
In Step 2, we built the **brains** of our Science Decoder Tool. We used FastAPI to create a web service to answer science questions. It uses SciBERT (an AI model) to understand scientific text and Facebook AI Similarity Search (FAISS) to search through information quickly. We tested it by asking it questions. We know it works because it returned the answers.

We need to give our tool a way to remember information we give it. We want it to remember the information after it's turned off, too. Think of it like giving our tool a notebook to write things down and retrieve them later. Instead of trying to keep everything in its head.

---

### **What We'll Build in Step 3**
1. Connect to a database (MongoDB) that can store information
2. Create a way to save scientific studies
3. Make it easy to find studies later
4. Add backup plans in case something goes wrong with the cloud database

---

### **Why This Matters**
Our tool forgets everthing when we shutdown the server. Imagine turning off your phone and having all the text messages disappear. We're adding MongoDB to our tool to ensure the content we add to the app will be there when we need it. It'll keep information safe for us to use it later. Databases are the reason your data, text messages and emails, are always there when you need them.

---

### **Step-by-Step Guide**

#### **Step 3.1: Set Up Your Project**

1. First, install the tools we need:
```bash
pip install pymongo python-dotenv
```

2. Create a new file called `.env` in your project folder and add these lines:
```
MONGODB_ATLAS_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
MONGODB_LOCAL_URI=mongodb://localhost:27017/
```

1. Replace `<username>`, `<password>`, and `<cluster>` with your MongoDB Atlas information. Do you need help setting up a free MongoDB Atlas account? Follow these steps:
   - Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - Sign up for a free account
   - Create a new cluster
   - Get your connection string from the "Connect" button
   - Here's a [video](https://youtu.be/VkXvVOb99g0?si=vnawmIzcKn62D0U0) showing how to do it!

#### **Step 3.2: Update Your Code**

Save the following code as `main.py`. This adds all the new features we need:

[Link to Step 3 `main.py` file on GitHub](https://i.til.show/science-clickbait-decoder-main-step-3)

#### **Step 3.3: Test Everything**

Time to test our code.
Open your terminal and follow these steps:

1. **Start your server**:
```bash
uvicorn main:app --reload
```

2. **Test saving a study**:
```bash
curl -X POST "http://127.0.0.1:8000/save-study" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Effects of Climate Change",
    "text": "This study discusses the impact of rising temperatures on ecosystems.",
    "topic": "Environment",
    "discipline": "Ecology"
  }'
```

The expected response:
```json
{"message": "Study saved successfully", "id": "12345..."}
```

3. **Find studies about the environment**:
```bash
curl "http://127.0.0.1:8000/get-studies/Environment"
```

The expected response to the curl command:
```json
{
  "studies": [
    {
      "_id": "12345...",
      "title": "The Effects of Climate Change",
      "text": "This study discusses the impact of rising temperatures on ecosystems.",
      "topic": "Environment",
      "discipline": "Ecology"
    }
  ]
}
```

Did something go wrong? Check:
- Is your MongoDB connection string correct in the `.env` file?
- Did you install all the required packages?
- Is your server running?
- Time to start debugging! Don't know how to debug? Check out this [article called "What is debugging?"](https://i.til.show/what-is-debugging-by-freecodecamp) by FreeCodeCamp
- Leave a comment below or send me a chat using the chat bubble at the bottom right corner of the screen. I'll try my best to respond and help you. Try debugging on your own first. It's a valuable skill to have.

---

### **What Makes This Approach Work So Well**
- **Always Safe**: Our data stays safe. Even if our server restarts.
- **Grows With You**: MongoDB can handle more information as our needs grow.
- **Backup Plan**: It automatically uses a local database as a backup if the cloud database (Atlas) isn't available.

### **Things to Watch Out For**
- Make sure to keep your MongoDB Atlas username and password secret!
- Test both saving and finding studies to ensure everything works
- Start with the free tier of MongoDB Atlas. You can upgrade later if more is needed.

---

### **What's Next?**
In Step 4, we'll make our tool even smarter! We'll combine MongoDB with FAISS to create a super-powered search system. This means our tool will understand how scientific studies and articles relate to each other. Not just remember scientific studies. It's like giving our tool the ability to connect dots between different pieces of information.

Stay tuned for more exciting features! If you need help, remember you can always:
- Check the MongoDB Atlas documentation
- Look at the FastAPI guides
- Ask questions in the MongoDB community forums
- Leave a comment telling me about your experience
- Reach out to me through the chat bubble at the bottom right corner of the screen

Did you miss the beginning of the Science Clickbait Decoder blog series?
Read Part 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0000).
Read Part 2 Step 1 [HERE](https://i.til.show/decoding-clickbait-science-articles-with-ai-0001). Part 2 Step 1 is when the coding starts.

*Excited about what’s coming? Share your progress so far and stay tuned for Step 3.*  

*If you have any questions or need help, feel free to ask.*
You may reach me by leaving a comment or clicking the chat bubble in the bottom right corner of the screen.

## Contact
For questions or inquiries, reach out at **a@awews.com**.
Chat with Brand Anthony McDonald in real-time by visiting
https://i.brandanthonymcdonald.com/portfolio
```
Text "CENT" to 833.752.8102 to join me on my journey to becoming the world's fastest centenarian.

Made with ❤️ by [BAM](https://i.brandanthonymcdonald.com/portfolio)

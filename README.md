### **Project Description**

This project is a **Retrieval-Augmented Generation (RAG) Tool** designed to help users better understand scientific studies and avoid misinformation propagated by clickbait or hyperbolic posts. The tool uses **free and open-source technologies** to provide insights, detect misinformation, and promote critical thinking when analyzing scientific claims.

Key features include:
- **NLP with Hugging Face SciBERT** to understand scientific text and communicate effectively with users from diverse socioeconomic backgrounds.
- **FAISS for fast vector similarity search**, ensuring quick retrieval of relevant study chunks.
- **MongoDB** for persistent storage of metadata, enabling advanced indexing by topic, discipline, and other dimensions.
- **Python FastAPI** to power backend services with minimal overhead and fast execution.
- **Next.js** for the frontend, enabling an interactive, SEO-friendly interface that supports RAG-based chat, multi-user support, and more.

The tool includes features like chunking, misinformation detection, bias awareness, and user feedback to iteratively improve accuracy and relevance. It supports multiple users, user invitations, and contribution forms for submitting scientific studies and articles for analysis.

The project emphasizes accessibility, transparency, and critical thinking by encouraging users to cross-reference multiple studies and learn from diverse perspectives.

---

### **README.md**

```markdown
# Retrieval-Augmented Generation (RAG) Tool for Scientific Literacy

## Introduction
This RAG tool is designed to combat misinformation by providing a clear and unbiased understanding of scientific studies. It leverages state-of-the-art Natural Language Processing (NLP) and information retrieval techniques to break down complex research papers and articles into accessible insights. The tool fosters critical thinking and transparency in science communication, making it valuable for individuals, researchers, and organizations aiming to understand the facts behind the headlines.

## Features
### 1. **Core Functionalities**
- **RAG-Based Chat**:
  - Engages users in meaningful conversations about scientific studies.
  - Allows users to **persist conversations** and invite others to participate.
  - Multi-user support with admin privileges to manage access.
- **Misinformation Detection**:
  - Identifies and flags misleading claims in scientific articles.
  - Provides context-aware summaries to highlight biases or gaps.
- **Bias Awareness**:
  - Informs users about potential biases in studies or claims.
- **User Feedback Loop**:
  - Users can rate responses for relevance, accuracy, and helpfulness to iteratively improve the system.

### 2. **Data Ingestion**
- **Article Submission**:
  - Submit article/blog links for review.
  - Cross-check citations to ensure alignment with claims.
- **Scientific Study Submission**:
  - Upload PDFs or provide links to studies.
  - Metadata stored for retrieval (e.g., topic, discipline).
- **Web Scraping**:
  - Uses BeautifulSoup to scrape and ingest content from websites.

### 3. **Text Processing**
- **Chunking**:
  - Breaks studies into smaller chunks for embedding.
  - Uses overlapping windows to maintain context during retrieval.
- **Indexing**:
  - FAISS ensures fast vector search for chunked data.
  - MongoDB stores metadata with indexing by topic, discipline, and other dimensions.

### 4. **Feedback and Continuous Improvement**
- Captures common user queries to improve FAQ-like responses.
- Encourages users to cross-reference studies for a balanced understanding.

---

## Technical Stack
### **Frontend**
- **Next.js**: Provides a modern, SEO-optimized, and interactive interface for:
  - Chat-based interactions.
  - User forms for invitations and submissions.
  - Deployment on **Vercel (free tier)** with a custom domain.

### **Backend**
- **Python FastAPI**: Powers the backend with:
  - API routes for interacting with FAISS and MongoDB.
  - Minimal overhead, fast execution, and modern API design.
- **BeautifulSoup**: Scrapes content from submitted links.

### **Data Storage and Retrieval**
- **FAISS**: Ensures high-speed vector similarity search for study embeddings.
- **MongoDB**: Stores metadata for persistent indexing and search.

### **NLP**
- **Hugging Face SciBERT**:
  - Pretrained on biomedical and scientific text.
  - Accessible for users with diverse backgrounds and educational levels.

---

## Deployment
### **Frontend**
- Hosted on **Vercel** (free tier) with a custom domain.
- Provides global content delivery, automatic SSL, and seamless integration with Next.js.

### **Backend**
- Options for hosting:
  1. **Render (free tier)**:
     - Ideal for Python-based FastAPI services.
  2. **Fly.io**:
     - Supports free-tier deployments with scalability options.
  3. **Deta**:
     - Free for lightweight FastAPI apps.

---

## Strengths of the Chosen Approach
### **1. Scalability and Speed**
- **FAISS**: Handles large datasets quickly, ensuring a smooth user experience.
- **MongoDB**: Persistent metadata allows efficient indexing and retrieval.

### **2. Accessibility**
- **Hugging Face SciBERT**: Tailored for scientific language, breaking down barriers for users from diverse backgrounds.

### **3. Developer Productivity**
- **Next.js**: Simplifies frontend development with built-in SSR and API routes.
- **FastAPI**: Reduces backend complexity with its modern design and fast execution.

### **4. User Engagement**
- Multi-user chat capabilities and forms for contributions foster collaboration and community building.

---

## Weaknesses of the Approach
### **1. Resource Limitations**
- **FAISS and MongoDB**: Combining these adds complexity, especially in synchronization and scalability.
- **Free Hosting**: Limited resources on free-tier platforms may impact performance during high usage.

### **2. Learning Curve**
- Next.js and FastAPI have slight learning curves, particularly for developers unfamiliar with SSR/modern APIs.

### **3. NLP Model Limitations**
- Hugging Face models like SciBERT might require fine-tuning for optimal performance with specific data.

---

## Getting Started

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/scientific-rag-tool.git
cd scientific-rag-tool
```

### **2. Install Dependencies**

#### Option 1: Using the Setup Script (Recommended)
We provide setup scripts for both Unix-based systems and Windows:

**For Windows:**
```powershell
# Open PowerShell as Administrator and first enable script execution (if not already enabled)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the setup script
.\setup.ps1
```

**For Unix-based systems (Linux/macOS):**
```bash
# Make the script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

The setup scripts will:
- Create and activate a Python virtual environment
- Check for GPU availability
- Install appropriate dependencies based on your choice:
  - Production: Minimal dependencies for running the application
  - Development: Includes testing tools, documentation generators, and development utilities
- Create a `.env` file from template

#### Option 2: Manual Installation

For production:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
venv\Scripts\activate.bat
# On Unix-based systems:
source venv/bin/activate

# Install production dependencies
pip install -r requirements.txt
```

For development:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
venv\Scripts\activate.bat
# On Unix-based systems:
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt
```

### **3. Environment Setup**
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` with your configuration values.

### **4. Run the Application**
Start the FastAPI backend:
```bash
uvicorn app.main:app --reload
```

Start the Next.js frontend:
```bash
npm run dev
```

### **5. Development Tools**
When installed with development dependencies (`requirements-dev.txt`), you have access to:
- **Testing**: `pytest` for running tests
- **Code Formatting**: `black` and `isort` for consistent code style
- **Type Checking**: `mypy` for static type analysis
- **Documentation**: `mkdocs` for generating documentation
- **Debugging**: Support through `debugpy`
- **Notebooks**: Jupyter notebooks for experimentation

Example development commands:
```bash
# Run tests
pytest

# Format code
black .
isort .

# Type checking
mypy .

# Generate documentation
mkdocs serve
```

### **6. Run Cache Script

# Clean files older than 7 days
`python scripts/manage_cache.py --action cleanup --max-age 7d`

# Clean files older than 24 hours
`python scripts/manage_cache.py --action cleanup --max-age 24h`

# Clean files older than 30 minutes
`python scripts/manage_cache.py --action cleanup --max-age 30m`

# View cleanup results in JSON:
`python scripts/manage_cache.py --action cleanup --max-age 7d --format json`

# Manual Clean-up
`python scripts/manage_cache.py --action stats`

# Clear model cache only
`python scripts/manage_cache.py --action clear --cache-type model`

# Clear all caches
`python scripts/manage_cache.py --action clear --cache-type all`

Get JSON output for automation:
`python scripts/manage_cache.py --action stats --format json`

Try clearing the cache and running the migration again:
# Clear caches
`python scripts/manage_cache.py --action clear`

# Run migration
`python -m app.migrations.run_migrations`


### **7. Deploy**
Follow deployment instructions for **Vercel** (frontend) and **Render/Fly.io** (backend).

---

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for improvements.

---

## Contact
For questions or inquiries, reach out at **a@awews.com**.
Chat with Brand Anthony McDonald in real-time by visiting
https://i.brandanthonymcdonald.com/portfolio
```

This README.md provides a comprehensive overview of the project, technical stack, features, deployment, and strengths/weaknesses for potential contributors and employers. Let me know if you'd like to refine or expand any sections!

Made with ❤️ by [BAM](https://brandanthonymcdonald.com/)
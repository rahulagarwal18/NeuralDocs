<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/LangChain-121212?style=for-the-badge&logo=chainlink&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
</p>

<h1 align="center">🧠 NeuralDocs: AI RAG Analyst</h1>

<p align="center">
  <b>A full-stack Retrieval-Augmented Generation (RAG) system for interrogating complex PDF documents.</b><br>
  <i>Extracts text, builds vector embeddings via FAISS, and utilizes LLMs to provide context-aware answers.</i>
</p>

---

## 📖 Overview

Standard AI models are restricted to their training data. **NeuralDocs** breaks this limitation by giving the AI long-term memory and specific context through **Retrieval-Augmented Generation (RAG)**.

Users can upload complex, massive PDF documents (such as legal contracts or research papers). The system intelligently chunks the text, calculates mathematical embeddings, and stores them in a highly-optimized FAISS vector database. When a query is asked, the system retrieves the most semantically relevant chunks and feeds them to the LLM to generate highly accurate, cited answers.

## ✨ Key Features

- 📄 **PDF Text Extraction**: Safely parses and cleans raw text from massive PDF documents.
- 🧩 **Semantic Chunking**: Uses recursive character splitting to preserve context across long paragraphs.
- 🧮 **Vector Database (FAISS)**: Calculates dense embeddings and performs lightning-fast similarity searches.
- 💬 **Interactive Chat Interface**: A stunning, responsive UI built with pure CSS glassmorphism.
- 🛠️ **Mock Mode / Sandbox**: Can run entirely locally without an API key using the built-in Mock fallback system for demonstration purposes.

---

## 🛠️ System Architecture

1. **Document Loader Pipeline**: `PyPDFLoader` extracts text -> `RecursiveCharacterTextSplitter` chunks it (1000 tokens, 200 overlap).
2. **Embedding Pipeline**: `OpenAIEmbeddings` transforms chunks into 1536-dimensional vectors.
3. **Storage**: Vectors are indexed into a local `FAISS` database.
4. **Retrieval Chain**: The user's query is embedded, compared against the FAISS index (Cosine Similarity), and the top $K$ chunks are injected into the LLM context window.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- An OpenAI API Key (Optional: Only required for full LLM execution, otherwise runs in Mock Mode)

```bash
# Clone the repository
git clone https://github.com/rahulagarwal18/NeuralDocs.git

# Navigate to the directory
cd NeuralDocs

# Install dependencies
pip install flask flask-cors werkzeug langchain openai faiss-cpu pypdf2

# Set your API Key (Optional)
export OPENAI_API_KEY="sk-your-key-here"
```

### Running the System
```bash
python app.py
```
*The web interface will launch locally at `http://127.0.0.1:5000`.*

---

<p align="center">
  Engineered with ❤️ by <a href="https://rahul-agarwal.in">Rahul Agarwal</a>
</p>

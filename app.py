import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

# Attempt to load RAG dependencies
try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_groq import ChatGroq
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MOCK_MODE = not bool(GROQ_API_KEY) or not LANGCHAIN_AVAILABLE

# Global state to hold the RAG pipeline
vector_store = None
qa_chain = None
uploaded_context = ""

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global vector_store, qa_chain, uploaded_context
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        if MOCK_MODE:
            uploaded_context = f"Document '{filename}' processed successfully."
            time.sleep(1.5)
            return jsonify({
                "message": f"Successfully processed {filename} (Mock Mode active)",
                "status": "ready"
            })
            
        try:
            # 1. Load PDF
            loader = PyPDFLoader(filepath)
            pages = loader.load()
            
            # 2. Chunk Text
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(pages)
            
            # 3. Create Local Embeddings & Store in FAISS
            # Using HuggingFace's extremely fast and efficient all-MiniLM-L6-v2 model (runs completely offline)
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vector_store = FAISS.from_documents(texts, embeddings)
            
            # 4. Initialize Groq LLM (Using powerful Llama-3-70b via Groq's free API)
            global global_llm, global_retriever
            global_llm = ChatGroq(
                temperature=0, 
                model_name="llama-3.3-70b-versatile", 
                groq_api_key=GROQ_API_KEY
            )
            global_retriever = vector_store.as_retriever()
            
            return jsonify({
                "message": f"Successfully processed {len(pages)} pages. Vector database initialized.",
                "status": "ready"
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid file type. Only PDF allowed."}), 400

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get("query", "")
    
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
        
    if MOCK_MODE:
        time.sleep(1)
        if not uploaded_context:
            return jsonify({"answer": "Please upload a document first before asking questions."})
        fake_response = f"Based on the mathematical embeddings of the uploaded document, the system has identified relevant context to answer your query: '{query}'. In a production environment, this text would be the synthesized LLM output."
        return jsonify({"answer": fake_response})
        
    if 'global_llm' not in globals() or 'global_retriever' not in globals():
        return jsonify({"error": "No document has been processed yet."}), 400
        
    try:
        # Retrieve context from FAISS
        docs = global_retriever.invoke(query)
        context_text = "\n\n".join([doc.page_content for doc in docs])
        
        # Build prompt and invoke Llama-3
        prompt = f"Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know.\n\nContext: {context_text}\n\nQuestion: {query}\n\nAnswer:"
        
        ai_msg = global_llm.invoke(prompt)
        return jsonify({"answer": ai_msg.content})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"Starting NeuralDocs... [MOCK_MODE: {MOCK_MODE}]")
    app.run(host='0.0.0.0', port=5000, debug=True)

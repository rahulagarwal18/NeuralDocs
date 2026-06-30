import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Optional/Advanced dependencies for RAG (will fail gracefully in Mock Mode)
try:
    from langchain.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import RetrievalQA
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if we should run in Mock Mode (No API keys required)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
MOCK_MODE = not bool(OPENAI_API_KEY) or not LANGCHAIN_AVAILABLE

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
        
        # --- MOCK MODE: Simulate Processing ---
        if MOCK_MODE:
            uploaded_context = f"Document '{filename}' processed successfully."
            time.sleep(1.5) # Simulate processing time
            return jsonify({
                "message": f"Successfully processed {filename} (Mock Mode active)",
                "status": "ready"
            })
            
        # --- PRODUCTION MODE: Actual RAG Pipeline ---
        try:
            # 1. Load PDF
            loader = PyPDFLoader(filepath)
            pages = loader.load()
            
            # 2. Chunk Text
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            texts = text_splitter.split_documents(pages)
            
            # 3. Create Embeddings & Store in FAISS
            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            vector_store = FAISS.from_documents(texts, embeddings)
            
            # 4. Initialize QA Chain
            llm = ChatOpenAI(temperature=0, model_name="gpt-4o", openai_api_key=OPENAI_API_KEY)
            qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vector_store.as_retriever())
            
            return jsonify({
                "message": f"Successfully processed {len(pages)} pages and created vector embeddings.",
                "status": "ready"
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid file type. Only PDF allowed."}), 400

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get("query", "")
    
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
        
    # --- MOCK MODE: Simulate AI Response ---
    if MOCK_MODE:
        time.sleep(1) # Simulate LLM latency
        if not uploaded_context:
            return jsonify({"answer": "Please upload a document first before asking questions."})
        
        fake_response = f"Based on the mathematical embeddings of the uploaded document, the system has identified relevant context to answer your query: '{query}'. In a production environment, this text would be the synthesized LLM output."
        return jsonify({"answer": fake_response})
        
    # --- PRODUCTION MODE: Query the RAG Pipeline ---
    if qa_chain is None:
        return jsonify({"error": "No document has been processed yet."}), 400
        
    try:
        response = qa_chain.run(query)
        return jsonify({"answer": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

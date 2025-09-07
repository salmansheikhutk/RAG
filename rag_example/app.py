"""
Flask RAG Application
Based on the Jupyter notebook RAG implementation
"""

from flask import Flask, request, jsonify, render_template
import json
import os
import numpy as np
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ✅ Configuration - Same as notebook
class RAGConfig:
    # OpenAI Settings
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GENERATION_MODEL = "gpt-4o-mini" 
    EMBEDDING_MODEL = "text-embedding-3-small"
    TEMPERATURE = 0.1
    MAX_TOKENS = 2000
    
    # Document Processing
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Files
    INPUT_DOCUMENTS = [
        "./documents/flintstone_api.json",
        "./documents/flintstone_api2.json"
    ]
    VECTOR_DATABASE_FILE = "vector_database.json"
    
    # RAG Settings
    TOP_K_RESULTS = 3

# Initialize OpenAI client
if not RAGConfig.OPENAI_API_KEY:
    raise ValueError("❌ Please set OPENAI_API_KEY in your .env file")

client = OpenAI(api_key=RAGConfig.OPENAI_API_KEY)

# Global variables for RAG components
vector_data = None
conversation_history = []

def json_to_text(data, indent=0):
    """🔄 Convert JSON to readable text format"""
    result = []
    prefix = "  " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            result.append(f"{prefix}{key}:")
            if isinstance(value, (dict, list)):
                result.append(json_to_text(value, indent + 1))
            else:
                result.append(f"{prefix}  {value}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                result.append(json_to_text(item, indent))
            else:
                result.append(f"{prefix}- {item}")
    
    return "\n".join(result)

def chunk_text(text: str) -> List[str]:
    """✂️ Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        # Get chunk of specified size
        end = start + RAGConfig.CHUNK_SIZE
        chunk = text[start:end]
        
        # If this isn't the last chunk, try to break at word boundary
        if end < len(text):
            last_space = chunk.rfind(' ')
            if last_space > 0:
                chunk = chunk[:last_space]
                end = start + last_space
        
        chunks.append(chunk.strip())
        
        # Move start position with overlap
        start = end - RAGConfig.CHUNK_OVERLAP
        
        # Prevent infinite loop if chunk overlap is too large
        if start >= end:
            start = end
    
    return chunks

def get_embedding(text: str) -> List[float]:
    """🧮 Get embedding vector for text using OpenAI"""
    try:
        response = client.embeddings.create(
            input=text,
            model=RAGConfig.EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Error getting embedding: {e}")
        return []

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """🧮 Calculate cosine similarity between two vectors"""
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    
    # Calculate dot product and magnitudes
    dot_product = np.dot(vec1_np, vec2_np)
    magnitude1 = np.linalg.norm(vec1_np)
    magnitude2 = np.linalg.norm(vec2_np)
    
    # Avoid division by zero
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)

def search_similar_chunks(question: str, top_k: int = None) -> List[Dict[str, Any]]:
    """🔍 Find most similar chunks to the question"""
    if top_k is None:
        top_k = RAGConfig.TOP_K_RESULTS
    
    # Get question embedding
    question_embedding = get_embedding(question)
    if not question_embedding:
        return []
    
    # Calculate similarities with all chunks
    results = []
    for chunk in vector_data["chunks"]:
        if not chunk.get("embedding"):
            continue
            
        similarity = cosine_similarity(question_embedding, chunk["embedding"])
        results.append({
            "chunk_id": chunk["id"],
            "text": chunk["text"],
            "similarity": similarity,
            "length": chunk["length"]
        })
    
    # Sort by similarity (highest first) and take top-k
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]

def generate_answer_with_history(question: str, context_chunks: List[Dict[str, Any]]) -> str:
    """🤖 Generate answer with conversation history"""
    # Combine context from chunks
    context = "\n\n".join([chunk["text"] for chunk in context_chunks])
    
    # Build conversation history string
    history_text = ""
    if conversation_history:
        history_text = "\n\nPREVIOUS CONVERSATION:\n"
        for i, (prev_q, prev_a) in enumerate(conversation_history[-3:]):  # Last 3 exchanges
            history_text += f"Q{i+1}: {prev_q}\nA{i+1}: {prev_a}\n\n"
    
    # Create enhanced prompt
    prompt = f"""Use the context to answer the question naturally and concisely.

CONTEXT:
{context}{history_text}

QUESTION: {question}

ANSWER:"""
    
    try:
        response = client.chat.completions.create(
            model=RAGConfig.GENERATION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=RAGConfig.MAX_TOKENS,
            temperature=RAGConfig.TEMPERATURE
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Store in conversation history
        conversation_history.append((question, answer))
        
        return answer
        
    except Exception as e:
        return f"Error generating answer: {e}"

def initialize_rag_system():
    """🚀 Initialize the RAG system - load or create vector database"""
    global vector_data
    
    # Try to load existing vector database
    if os.path.exists(RAGConfig.VECTOR_DATABASE_FILE):
        print("📖 Loading existing vector database...")
        with open(RAGConfig.VECTOR_DATABASE_FILE, 'r', encoding='utf-8') as f:
            vector_data = json.load(f)
        print(f"✅ Loaded {len(vector_data['chunks'])} chunks from database")
        return True
    
    # Create new vector database
    print("🔄 Creating new vector database...")
    
    # Load and process all documents
    all_document_text = ""
    processed_files = []
    
    for doc_path in RAGConfig.INPUT_DOCUMENTS:
        if os.path.exists(doc_path):
            print(f"📄 Processing {doc_path}...")
            with open(doc_path, 'r', encoding='utf-8') as file:
                raw_json_data = json.load(file)
            
            # Convert JSON to text with file identifier
            document_text = f"--- Document: {doc_path} ---\n"
            document_text += json_to_text(raw_json_data)
            document_text += f"\n--- End of {doc_path} ---\n\n"
            
            all_document_text += document_text
            processed_files.append(doc_path)
        else:
            print(f"⚠️ Warning: File not found - {doc_path}")
    
    if not all_document_text:
        print("❌ No documents found to process!")
        return False
    
    print(f"✅ Successfully loaded {len(processed_files)} documents")
    
    # Create chunks from combined text
    text_chunks_list = chunk_text(all_document_text)
    chunks_with_metadata = []
    
    for i, chunk in enumerate(text_chunks_list):
        chunk_data = {
            "id": i,
            "text": chunk,
            "length": len(chunk),
            "start_pos": i * (RAGConfig.CHUNK_SIZE - RAGConfig.CHUNK_OVERLAP)
        }
        chunks_with_metadata.append(chunk_data)
    
    # Generate embeddings
    print(f"🧮 Generating embeddings for {len(chunks_with_metadata)} chunks...")
    successful_embeddings = 0
    
    for i, chunk in enumerate(chunks_with_metadata):
        print(f"Processing chunk {i+1}/{len(chunks_with_metadata)}...")
        
        embedding = get_embedding(chunk["text"])
        if embedding:
            chunk["embedding"] = embedding
            chunk["embedding_size"] = len(embedding)
            successful_embeddings += 1
        else:
            chunk["embedding"] = []
            chunk["embedding_size"] = 0
    
    # Create vector database structure
    vector_data = {
        "metadata": {
            "source_documents": processed_files,
            "chunk_size": RAGConfig.CHUNK_SIZE,
            "chunk_overlap": RAGConfig.CHUNK_OVERLAP,
            "embedding_model": RAGConfig.EMBEDDING_MODEL,
            "total_chunks": len(chunks_with_metadata),
            "created_at": "2025-09-06"
        },
        "chunks": []
    }
    
    # Add only chunks with successful embeddings
    for chunk in chunks_with_metadata:
        if chunk.get("embedding"):
            vector_data["chunks"].append({
                "id": chunk["id"],
                "text": chunk["text"],
                "length": chunk["length"],
                "start_pos": chunk["start_pos"],
                "embedding": chunk["embedding"]
            })
    
    # Save vector database
    with open(RAGConfig.VECTOR_DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(vector_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Vector database created with {len(vector_data['chunks'])} chunks")
    return True

# Flask routes
@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Search for relevant chunks
        search_results = search_similar_chunks(question)
        
        if not search_results:
            return jsonify({
                'answer': 'I couldn\'t find relevant information for that question.',
                'chunks_used': 0,
                'similarities': []
            })
        
        # Generate answer with conversation history
        answer = generate_answer_with_history(question, search_results)
        
        return jsonify({
            'answer': answer,
            'chunks_used': len(search_results),
            'similarities': [round(r['similarity'], 3) for r in search_results],
            'question': question
        })
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return jsonify({'message': 'History cleared'})

@app.route('/api/status')
def status():
    """Get system status"""
    return jsonify({
        'status': 'ready' if vector_data else 'not_initialized',
        'chunks_loaded': len(vector_data['chunks']) if vector_data else 0,
        'conversation_length': len(conversation_history),
        'model': RAGConfig.GENERATION_MODEL,
        'embedding_model': RAGConfig.EMBEDDING_MODEL
    })

if __name__ == '__main__':
    # Initialize RAG system on startup
    print("🚀 Initializing RAG System...")
    if initialize_rag_system():
        print("✅ RAG system ready!")
        print("🌐 Starting Flask server...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Failed to initialize RAG system")

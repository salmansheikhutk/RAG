from flask import Flask, render_template, request, jsonify
import os
import sys
from pathlib import Path

# Add the current directory to the Python path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from document_qa_system import DocumentRAGSystem
import config

app = Flask(__name__)

# Initialize the RAG system
qa_system = None

def initialize_qa_system():
    """Initialize the Q&A system"""
    global qa_system
    try:
        qa_system = DocumentRAGSystem()
        
        # Try to load existing knowledge base
        if not qa_system.load_existing_knowledge_base():
            print("📚 No existing knowledge base found. Building new one...")
            qa_system.build_knowledge_base()
        else:
            print("📚 Loaded existing knowledge base successfully!")
            
        print("✅ Document Q&A System initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Error initializing Q&A system: {e}")
        return False

def get_document_count():
    """Get the number of documents loaded"""
    try:
        documents_path = Path(config.DOCUMENTS_PATH)
        if documents_path.exists():
            doc_files = [
                f for f in documents_path.glob("**/*") 
                if f.is_file() and f.suffix.lower() in config.SUPPORTED_EXTENSIONS
            ]
            return len(doc_files)
        return 0
    except Exception:
        return 0

@app.route('/')
def index():
    """Render the main chat interface"""
    document_count = get_document_count()
    return render_template('index.html', document_count=document_count)

@app.route('/ask', methods=['POST'])
def ask_question():
    """Handle question submission and return answer"""
    global qa_system
    
    try:
        # Get the question from the request
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'Please provide a question'
            })
        
        # Initialize QA system if not already done
        if qa_system is None:
            if not initialize_qa_system():
                return jsonify({
                    'success': False,
                    'error': 'Failed to initialize Q&A system. Please check your documents and configuration.'
                })
        
        # Get the answer
        print(f"🔍 Processing question: {question}")
        
        # Use the ask_question method from DocumentRAGSystem
        response = qa_system.ask_question(question)
        
        # The ask_question method returns a dictionary with 'answer', 'sources', etc.
        if 'error' in response:
            return jsonify({
                'success': False,
                'error': response.get('answer', 'An error occurred')
            })
        
        # Extract answer and sources from the response dictionary
        answer = response.get('answer', 'No answer provided')
        raw_sources = response.get('sources', [])
        
        # Convert sources to the format expected by the web interface
        sources = []
        for source in raw_sources[:3]:  # Limit to top 3 sources
            # Each source should be a dict with content and metadata
            if isinstance(source, dict):
                source_name = source.get('source_file', 'Unknown document')
                source_content = source.get('content', '')[:200] + ('...' if len(source.get('content', '')) > 200 else '')
                
                sources.append({
                    'name': source_name,
                    'content': source_content
                })
        
        return jsonify({
            'success': True,
            'answer': answer,
            'sources': sources
        })
        
    except Exception as e:
        print(f"❌ Error processing question: {e}")
        return jsonify({
            'success': False,
            'error': f'An error occurred while processing your question: {str(e)}'
        })

@app.route('/status')
def status():
    """Return system status"""
    global qa_system
    
    return jsonify({
        'qa_system_initialized': qa_system is not None,
        'document_count': get_document_count(),
        'documents_path': config.DOCUMENTS_PATH,
        'vector_store_path': config.VECTOR_STORE_PATH,
        'model_name': config.MODEL_NAME
    })

if __name__ == '__main__':
    print("🚀 Starting Document Q&A Web Application...")
    print("📁 Documents path:", config.DOCUMENTS_PATH)
    print("🗄️ Vector store path:", config.VECTOR_STORE_PATH)
    print(f"📊 Found {get_document_count()} documents")
    
    # Initialize the QA system on startup
    print("🤖 Initializing Q&A system...")
    initialize_qa_system()
    
    print("🌐 Starting Flask web server...")
    print("💻 Open your browser to: http://127.0.0.1:5000")
    
    app.run(debug=True, host='127.0.0.1', port=5000)

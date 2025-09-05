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
        
        # Use the ask_question method from DocumentQASystem
        full_response = qa_system.ask_question(question)
        
        # Parse the response to extract answer and sources
        if "📄 Sources" in full_response:
            parts = full_response.split("📄 Sources")
            answer = parts[0].replace("🤖 Answer:\n", "").strip()
            sources_text = parts[1] if len(parts) > 1 else ""
            
            # Parse sources (simplified - could be enhanced)
            sources = []
            if sources_text:
                # Extract source information (this is a simplified parser)
                lines = sources_text.split('\n')
                current_source = None
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('---'):
                        if line.endswith(('.md)', '.json)', '.pdf)', '.txt)', '.docx)')):
                            # This looks like a source name
                            if current_source:
                                sources.append(current_source)
                            
                            # Extract filename
                            filename = line.split('(')[-1].replace(')', '').strip()
                            current_source = {
                                'name': filename,
                                'content': ''
                            }
                        elif current_source and line and not line.startswith('  '):
                            # This is content for the current source
                            if len(current_source['content']) < 200:  # Limit content length
                                current_source['content'] += line + ' '
                
                # Add the last source
                if current_source and current_source not in sources:
                    sources.append(current_source)
                
                # Clean up source content
                for source in sources:
                    source['content'] = source['content'].strip()[:200] + ('...' if len(source['content']) > 200 else '')
        else:
            # No sources found, just return the answer
            answer = full_response.replace("🤖 Answer:\n", "").strip()
            sources = []
        
        return jsonify({
            'success': True,
            'answer': answer,
            'sources': sources[:3]  # Limit to top 3 sources
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

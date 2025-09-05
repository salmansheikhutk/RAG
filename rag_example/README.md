# Document Q&A System - Simple RAG Implementation

A straightforward RAG (Retrieval-Augmented Generation) system for searching and answering questions from technical documents.

## 🔄 **RAG Workflow**

```
1. Documents → 2. Text Chunking → 3. Embeddings → 4. Vector Database → 5. Search & Generate
```

**Step by Step:**
1. **Load Documents** - PDF, markdown, text, JSON files from `documents/` folder
2. **Split into Chunks** - Break documents into 1500-character searchable pieces  
3. **Create Embeddings** - Convert text chunks to vectors using OpenAI embeddings
4. **Store in Database** - Save vectors in ChromaDB for fast similarity search
5. **Answer Questions** - Find relevant chunks + generate answers with GPT-3.5

## ⚙️ **Technical Setup**

### **Core Technologies**
- **LangChain**: RAG pipeline orchestration
- **ChromaDB**: Vector database for embeddings
- **OpenAI**: text-embedding-ada-002 + gpt-3.5-turbo
- **Document Loaders**: PDF, markdown, text, JSON support

### **Key Settings** (`config.py`)
```python
CHUNK_SIZE = 1500          # Text chunk size
CHUNK_OVERLAP = 300        # Overlap between chunks  
RAG_TOP_K_RESULTS = 5      # Documents retrieved per query
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 0.1          # Low = more factual answers
```

## 🚀 **How to Run**

### **Option 1: Web Interface (Recommended)**
```bash
# Install dependencies
pip install -r requirements.txt

# Set API key in .env file
echo "OPENAI_API_KEY=your-openai-key-here" > .env

# Start the web application
python app.py
```

**Then open your browser to: http://127.0.0.1:5000**

### **Option 2: Command Line Interface**
```bash
python document_qa_system.py
```

## 📁 **File Structure**
```
rag_example/
├── app.py                     # Flask web application  
├── document_qa_system.py      # Command-line interface
├── config.py                  # Configuration settings
├── requirements.txt           # Dependencies
├── run.py                     # Simple run script
├── templates/
│   └── index.html            # Web interface HTML
├── static/
│   └── style.css             # Web interface styles
├── documents/                # Put your documents here
│   ├── api_documentation.md
│   ├── product_manual_xr450.md
│   ├── compliance_report.md
│   └── flintstone_api.json
└── document_knowledge_base/   # Auto-created vector database
```

## ⚡ **Features**
- **🌐 Beautiful Web Interface**: Modern, responsive design
- **💬 Interactive Chat**: Real-time question and answer
- **📄 Source Attribution**: See which documents contain answers
- **📱 Mobile Friendly**: Works on all devices
- **⚡ Fast Search**: Sub-2-second response times
- **🔄 Auto-Rebuild**: Automatically processes new documents

That's it! The system will automatically process your documents and be ready for questions in under 30 seconds.

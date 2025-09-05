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

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Set API Key**
Create `.env` file:
```bash
OPENAI_API_KEY=your-openai-key-here
```

### **3. Add Documents**
Put your files in the `documents/` folder:
```
documents/
├── api_documentation.md
├── product_manual.pdf  
├── troubleshooting.txt
└── compliance_report.docx
```

### **4. Run the System**
```bash
python document_qa_system.py
```

### **5. Ask Questions**
```
📋 Question: How do I configure SSL encryption?
🤖 Answer: According to the API documentation, SSL encryption is configured by...

📋 Question: What are the system requirements?
🤖 Answer: The product manual specifies the following requirements...
```

## 📁 **File Structure**
```
rag_example/
├── document_qa_system.py    # Main application
├── config.py               # Configuration settings
├── requirements.txt        # Dependencies
├── documents/             # Put your documents here
└── document_knowledge_base/ # Auto-created vector database
```

## ⚡ **Quick Commands**
- **Start**: `python document_qa_system.py`
- **Check Status**: Type `status` in the Q&A interface
- **Exit**: Type `quit`
- **Rebuild Database**: Delete `document_knowledge_base/` folder and restart

That's it! The system will automatically process your documents and be ready for questions in under 30 seconds.

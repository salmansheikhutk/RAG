# Technical Document Q&A System

This directory contains a **simplified RAG system** designed for technical document Q&A - perfect for the business use case of searching through thousands of technical documents.

## 🎯 **Business Problem Solved**

- **Wasted Time**: Instant semantic search instead of manual browsing
- **Frustration**: Relevant, context-aware answers instead of keyword-only results  
- **Missed Opportunities**: AI understands natural language questions
- **Inconsistent Formats**: Unified search across PDFs, docs, text files

## 🚀 **Quick Start**

### **1. Setup**
```bash
# Install dependencies (same as main project)
pip install -r ../requirements.txt

# Copy your .env file
cp ../.env .
```

### **2. Add Your Documents**
```bash
# Put your technical documents in the documents/ folder:
documents/
├── manuals/
│   ├── product_manual_v2.pdf
│   └── installation_guide.md
├── specs/
│   ├── technical_specs.docx
│   └── api_documentation.txt
├── faqs/
│   └── troubleshooting_guide.md
└── compliance/
    └── compliance_report.pdf
```

### **3. Run the System**
```bash
python document_qa_system.py
```

### **4. Ask Questions**
```
📋 Question: How do I troubleshoot error code E404?
🤖 Answer: Based on the troubleshooting guide, error E404 typically indicates...

📋 Question: What are the compliance requirements for product X?
🤖 Answer: According to the compliance report, product X must meet...

📋 Question: Show me the installation steps
🤖 Answer: The installation guide specifies the following steps...
```

## 📊 **Features**

### **🔍 Smart Search**
- **Semantic Understanding**: Finds relevant info even with different terminology
- **Multi-Document Search**: Searches across all document types simultaneously
- **Source Attribution**: Shows exactly which documents contain the answer

### **💬 Natural Language Interface**
- Ask questions in plain English
- No need to learn complex search syntax
- Context-aware responses

### **📄 Document Support**
- PDF files (`.pdf`)
- Text files (`.txt`)
- Markdown files (`.md`)
- Word documents (`.docx`)
- JSON files (`.json`)

### **⚡ Performance**
- Instant responses (< 2 seconds)
- Persistent knowledge base (rebuild only when documents change)
- Configurable chunk sizes for optimal retrieval

## 🔧 **Configuration**

Edit `config.py` to customize:

```python
# Document processing
CHUNK_SIZE = 1500          # Size of text chunks
CHUNK_OVERLAP = 300        # Overlap between chunks
RAG_TOP_K_RESULTS = 5      # Number of relevant chunks to retrieve

# Answer formatting  
INCLUDE_SOURCES = True     # Show source documents
MAX_SOURCES_DISPLAY = 3    # Max sources to display
ANSWER_MAX_LENGTH = 2000   # Max answer length
```

## 🏗️ **Architecture**

```
Documents → Document Loader → Text Chunking → Embeddings → Vector DB → Q&A Chain
```

### **Key Components**:
- **Document Loader**: Handles multiple file formats
- **Text Splitter**: Breaks documents into searchable chunks  
- **Vector Store**: ChromaDB for persistent storage
- **Embeddings**: OpenAI text-embedding-ada-002
- **Q&A Chain**: GPT-3.5-turbo for answer generation

## 💡 **Usage Examples**

### **Technical Support**
```
📋 Question: Customer reports system crashes on startup
🤖 Answer: [Searches troubleshooting guides, installation manuals, known issues]
```

### **Product Information**
```  
📋 Question: What are the power requirements for Model XR-450?
🤖 Answer: [Searches technical specifications, product manuals]
```

### **Compliance Queries**
```
📋 Question: What safety certifications does our product have?
🤖 Answer: [Searches compliance reports, certification documents]
```

## 🎯 **Business Impact**

- **⚡ Speed**: Seconds instead of hours to find information
- **🎯 Accuracy**: Context-aware answers instead of irrelevant results
- **📈 Productivity**: Technical teams spend time solving problems, not searching
- **😊 Satisfaction**: Employees and customers get quick, accurate answers
- **💰 Cost Savings**: Reduced support escalation and operational delays

## 🔄 **Comparison with Full Agent System**

| Feature | Full Agent System | Document Q&A System |
|---------|-------------------|---------------------|
| **Purpose** | Infrastructure automation | Document search & Q&A |
| **Complexity** | Multi-step workflows | Simple question → answer |
| **Integration** | ServiceNow, GitHub, AWS | Standalone document search |
| **User Interface** | Tool + Chat modes | Chat-only interface |
| **Use Case** | DevOps automation | Knowledge management |

This simplified system focuses purely on **document Q&A** - perfect for the business use case! 🚀

# IICS RAG Assistant

A Retrieval-Augmented Generation (RAG) assistant for Informatica Intelligent Cloud Services (IICS) documentation.

## Features

- 📖 **PDF Document Processing**: Load and process IICS documentation PDF
- 🔍 **Intelligent Search**: Find relevant information using semantic similarity
- 🤖 **AI-Powered Answers**: Get contextual answers using OpenAI's GPT models
- 💾 **Vector Storage**: Persistent storage using ChromaDB
- 💬 **Interactive CLI**: Simple command-line interface

## Setup

### 1. Prerequisites
- Python 3.8 or higher
- OpenAI API key

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd RAG

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate    # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. Add your OpenAI API key to the `.env` file:
```
OPENAI_API_KEY=your_actual_api_key_here
```

2. Make sure `IICS_documentation.pdf` is in the project root directory

## Usage

### Basic Usage

```bash
# Run the interactive assistant
python main.py

# Force reload documentation (if you updated the PDF)
python main.py --reload

# Run demo questions
python main.py --demo
```

### Example Questions

- "What is IICS?"
- "How do I create a mapping in IICS?"
- "What are the different types of connections available?"
- "How do I configure a secure agent?"
- "What is the difference between a mapping and a mapping task?"
- "How do I set up data quality rules?"

## Architecture

```
PDF Document → Text Chunks → Embeddings → Vector Store → Similarity Search → LLM Response
```

1. **Document Loading**: PDF is loaded and split into manageable chunks
2. **Embedding Creation**: Each chunk is converted to vector embeddings
3. **Vector Storage**: Embeddings stored in ChromaDB for fast similarity search
4. **Query Processing**: User questions are embedded and matched against stored chunks
5. **Answer Generation**: Relevant chunks are sent to GPT for contextual answers

## Project Structure

```
RAG/
├── IICS_documentation.pdf    # Your IICS documentation
├── requirements.txt          # Python dependencies
├── config.py                # Configuration settings
├── rag_assistant.py         # Main RAG implementation
├── main.py                  # CLI interface
├── .env                     # Environment variables (API keys)
├── venv/                    # Virtual environment
└── chroma_db/              # Vector database (created automatically)
```

## Configuration Options

Edit `config.py` to customize:

- `CHUNK_SIZE`: Size of text chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `MAX_TOKENS`: Maximum tokens for LLM response (default: 4000)
- `TEMPERATURE`: LLM creativity level (default: 0.3)

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Make sure your API key is correctly set in `.env`
   - Check that you have credits in your OpenAI account

2. **PDF Not Found**
   - Ensure `IICS_documentation.pdf` is in the project root
   - Check the file name matches exactly

3. **Memory Issues**
   - Reduce `CHUNK_SIZE` if processing large documents
   - Consider processing documents in smaller batches

## Extending the System

### Adding New Documents
```python
# Add more documents to the vector store
assistant.load_additional_documents(['new_doc.pdf'])
```

### Custom Prompts
Modify the prompt template in `rag_assistant.py` for specific use cases.

### Different Models
Change the OpenAI model in `config.py`:
```python
# Use GPT-4 for better answers (more expensive)
model_name="gpt-4"
```

## Cost Considerations

- **Embedding costs**: ~$0.0001 per 1K tokens for text-embedding-ada-002
- **LLM costs**: ~$0.002 per 1K tokens for GPT-3.5-turbo
- Typical document processing: $1-5 for a 200-page PDF
- Per query: $0.01-0.05 depending on context length

## License

MIT License - see LICENSE file for details.

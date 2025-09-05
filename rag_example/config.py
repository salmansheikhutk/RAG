# Technical Document Q&A System Configuration

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

# RAG Configuration
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300
RAG_TOP_K_RESULTS = 5

# Document Processing
DOCUMENTS_PATH = "./documents"
VECTOR_STORE_PATH = "./document_knowledge_base"  # Separate from agent system

# AI Model Configuration
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 0.1  # Low temperature for accurate information retrieval
MAX_TOKENS = 4000

# Supported Document Types
SUPPORTED_EXTENSIONS = [".txt", ".md", ".pdf", ".docx", ".json"]

# Answer Formatting
INCLUDE_SOURCES = True
MAX_SOURCES_DISPLAY = 3
ANSWER_MAX_LENGTH = 2000

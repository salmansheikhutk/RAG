# Configuration for IICS RAG Assistant
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_TOKENS = 4000
TEMPERATURE = 0.3

# Vector Store Configuration
VECTOR_STORE_PATH = "./chroma_db"

# Document Configuration
PDF_PATH = "./IICS_documentation.pdf"

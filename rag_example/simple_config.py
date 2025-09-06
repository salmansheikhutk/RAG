"""
Simple RAG Configuration - No LangChain
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

# Model Configuration
GENERATION_MODEL = "gpt-3.5-turbo"
EMBEDDING_MODEL = "text-embedding-ada-002"
TEMPERATURE = 0.1
MAX_TOKENS = 2000

# Document Processing Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Simple Vector Database Configuration
VECTOR_DATABASE_FILE = "vector_database.json"
INPUT_DOCUMENT = "./documents/flintstone_api.json"

# RAG Configuration
TOP_K_RESULTS = 3

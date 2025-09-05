# Configuration for S3 Bucket Creation Agent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set OPENAI_API_KEY in your .env file")

# Mock API Configuration (set to True for real APIs)
USE_REAL_SERVICENOW = os.getenv("USE_REAL_SERVICENOW", "False").lower() == "true"
USE_REAL_GITHUB = os.getenv("USE_REAL_GITHUB", "False").lower() == "true"
USE_REAL_AWS = os.getenv("USE_REAL_AWS", "False").lower() == "true"

# API Keys (optional - for real integrations)
SERVICENOW_INSTANCE = os.getenv("SERVICENOW_INSTANCE", "mock.service-now.com")
SERVICENOW_USERNAME = os.getenv("SERVICENOW_USERNAME", "mock_user")
SERVICENOW_PASSWORD = os.getenv("SERVICENOW_PASSWORD", "mock_pass")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "mock_github_token")
GITHUB_REPO = os.getenv("GITHUB_REPO", "company/infrastructure")
GITHUB_TARGET_BRANCH = os.getenv("GITHUB_TARGET_BRANCH", "dev")  # Target branch for PRs

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "mock_access_key")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "mock_secret")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Agent Configuration
TEMPERATURE = 0.1  # Low temperature for more consistent decisions
MAX_TOKENS = 4000
MODEL_NAME = "gpt-3.5-turbo"

# RAG Configuration
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300
VECTOR_STORE_PATH = "./agent_knowledge_base"
CHROMA_DB_PATH = "./chroma_db"  # Now local to this project
RAG_TOP_K_RESULTS = 5

# Data Paths
TICKETS_PATH = "./data/tickets"
REPO_PATTERNS_PATH = "./data/repo_patterns"
COMPANY_DOCS_PATH = "./data/company_docs"

# Company Standards
DEFAULT_REGION = "us-east-1"
COMPANY_TAGS = {
    "ManagedBy": "CloudInfrastructureTeam",
    "Organization": "CompanyName",
    "DeployedBy": "S3CreationAgent"
}

# Approval Thresholds
AUTO_APPROVE_COST_LIMIT = 100  # USD per month
REQUIRES_SECURITY_REVIEW = ["prod", "production"]
REQUIRES_BUSINESS_APPROVAL = 500  # USD per month

# S3 Bucket Creation Agent

An intelligent AI agent that automates AWS S3 bucket provisioning from ServiceNow tickets using Retrieval-Augmented Generation (RAG) and multi-tool orchestration.

## 🚀 Features

### **Agentic AI Workflow**
- 🎫 **ServiceNow Integration**: Reads and processes ticket requests
- 🧠 **Intelligent Requirements Extraction**: Uses AI to understand business needs
- � **RAG-Powered Knowledge Search**: Searches company standards and patterns
- ⚙️ **Automated Code Generation**: Creates Terraform configurations
- � **GitHub Integration**: Creates pull requests for human approval
- 👥 **Human-in-the-Loop**: Maintains oversight and approval workflow

### **Knowledge Base**
- Company AWS standards and naming conventions
- Terraform templates and IAM policies  
- Security and compliance requirements
- Historical ticket patterns and solutions
- Cost optimization guidelines

### **Multi-Tool Architecture**
- **ServiceNow Reader**: Mock/real ServiceNow API integration
- **RAG Searcher**: Company knowledge base search
- **S3 Config Generator**: Terraform configuration generation
- **GitHub Tools**: Repository search and PR creation
- **Requirements Extractor**: Structured requirement parsing

## 🏗️ Architecture

```
ServiceNow Ticket → AI Agent → RAG Knowledge Base → Terraform Config → GitHub PR → Human Approval
```

### **Workflow Steps**
1. **Read Ticket**: Extract S3 bucket requirements from ServiceNow
2. **Analyze Requirements**: Use AI to structure and validate needs
3. **Search Knowledge**: Find relevant company standards via RAG
4. **Generate Config**: Create Terraform code following best practices
5. **Create PR**: Submit for human review and approval
6. **Deploy**: Automated deployment after approval

## 📁 Project Structure

```
RAG/
├── agent/
│   ├── core/
│   │   └── s3_agent.py          # Main agent orchestrator
│   └── tools/
│       ├── servicenow_tools.py  # ServiceNow integration
│       ├── rag_tools.py         # Knowledge base search
│       ├── s3_generator.py      # Terraform generation
│       └── github_tools.py      # GitHub integration
├── data/
│   ├── tickets/                 # Mock ServiceNow tickets
│   ├── repo_patterns/           # Terraform templates
│   └── company_docs/            # Standards and policies
├── agent_config.py              # Configuration
├── main.py                      # CLI application
└── requirements.txt             # Dependencies
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and setup
git clone <repo-url>
cd RAG

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the Agent

```bash
# Interactive mode
python main.py

# Demo mode (automated scenarios)
python main.py --demo
```

## 💻 Usage Examples

### **Process a ServiceNow Ticket**
```bash
Agent> process RITM001234
```
The agent will:
- Read the ticket requirements
- Search company knowledge base
- Generate Terraform configuration
- Create GitHub pull request
- Provide approval workflow

### **Search Knowledge Base**
```bash
Agent> search "s3 backup policies"
Agent> search "terraform encryption standards"
```

### **List Open Tickets**
```bash
Agent> list-tickets
```

### **Check Agent Status**
```bash
Agent> status
```

## 📊 Example Workflow

**Input**: ServiceNow ticket requesting S3 bucket for analytics
**Output**: Complete infrastructure-as-code solution

```yaml
Ticket: RITM001234 - Analytics bucket needed
↓
Requirements Extracted:
  - Bucket: analytics-customer-data-prod  
  - Environment: Production
  - Encryption: AES-256
  - Versioning: Required
  - Compliance: GDPR, SOX
↓  
Knowledge Base Search:
  - Found: naming conventions
  - Found: security policies
  - Found: Terraform templates
↓
Generated Configuration:
  - main.tf (bucket resource)
  - variables.tf (parameters)
  - outputs.tf (resource outputs)
↓
GitHub PR Created:
  - Branch: s3-bucket/ritm001234-analytics
  - Reviewers: Infrastructure & Security teams
  - Auto-deployment ready
```

## 🔧 Configuration Options

Edit `agent_config.py` to customize:

```python
# API Integration (set to True for real APIs)
USE_REAL_SERVICENOW = False  # Mock by default
USE_REAL_GITHUB = False      # Mock by default  
USE_REAL_AWS = False         # Mock by default

# AI Configuration
MODEL_NAME = "gpt-3.5-turbo"  # Or "gpt-4" for better results
TEMPERATURE = 0.1             # Low for consistent decisions

# Cost Thresholds
AUTO_APPROVE_COST_LIMIT = 100      # USD/month
REQUIRES_BUSINESS_APPROVAL = 500   # USD/month
```

## 🗄️ Knowledge Base

The agent learns from:

### **ServiceNow Tickets** (`data/tickets/`)
- Real examples of S3 bucket requests
- Requirements patterns and common scenarios
- Business justifications and use cases

### **Repository Patterns** (`data/repo_patterns/`)
- Terraform templates for different bucket types
- IAM policies for various access patterns
- Infrastructure-as-code best practices

### **Company Standards** (`data/company_docs/`)
- Naming conventions and tagging requirements
- Security and compliance policies
- Approval workflows and cost guidelines

## 🔍 RAG System Details

- **Embedding Model**: OpenAI text-embedding-ada-002
- **Vector Store**: ChromaDB (persistent storage)
- **Chunk Size**: 1,500 characters with 300 overlap
- **Search Strategy**: Semantic similarity + keyword matching
- **Context Integration**: Multi-document synthesis

## 🛡️ Security & Compliance

- **Encryption**: Automatic AES-256 or KMS configuration
- **Public Access**: Always blocked by default
- **IAM Policies**: Least-privilege access patterns
- **Compliance**: GDPR/SOX/HIPAA/PCI support
- **Audit Trail**: All decisions logged and traceable

## 💰 Cost Management

- **Auto-Approval**: <$100/month requests
- **Business Approval**: >$500/month requires stakeholder review
- **Cost Estimation**: AI-powered based on usage patterns
- **Optimization**: Lifecycle policies and storage classes

## 🔄 Development & Testing

### **Add New Ticket Scenarios**
```bash
# Add to data/tickets/
{
  "ticket_id": "RITM001237",
  "description": "New S3 use case...",
  ...
}
```

### **Extend Knowledge Base**
```bash
# Add to data/company_docs/ or data/repo_patterns/
# Agent automatically reindexes on restart
```

### **Test Individual Tools**
```python
from agent.tools.s3_generator import S3ConfigGenerator

generator = S3ConfigGenerator()
config = generator._run("production analytics bucket with encryption")
```

## 🤝 Integration Options

- **ServiceNow**: Real API integration with pysnow
- **GitHub**: PyGithub for repository management  
- **AWS**: Boto3 for validation and deployment
- **Slack/Teams**: Notification integrations
- **JIRA**: Alternative ticket system support

## 📈 Metrics & Monitoring

The agent tracks:
- Ticket processing time and success rate
- Cost accuracy and approval patterns
- Security compliance adherence
- Human review feedback integration
- Knowledge base search effectiveness

## 🛠️ Troubleshooting

**Common Issues:**
1. **RAG not finding relevant info**: Add more examples to knowledge base
2. **Terraform validation errors**: Check company standards alignment
3. **API rate limits**: Configure delays and retry logic
4. **Missing requirements**: Improve ticket requirement extraction

## 🔮 Future Enhancements

- Multi-cloud support (Azure, GCP)
- Advanced cost optimization recommendations
- Automated security scanning integration
- Real-time collaboration features
- Machine learning from approval feedback

## 📄 License

MIT License - see LICENSE file for details.

# S3 Bucket Creation Agent - Complete System

This directory contains the **complete agentic AI system** for automating S3 bucket creation and IAM policy management from ServiceNow tickets.

## 🤖 **What This System Does**

- **Reads ServiceNow tickets** and processes infrastructure requests
- **Intelligently classifies** request types (S3 bucket creation vs IAM policy updates)
- **Searches company knowledge base** using RAG for compliance patterns
- **Generates Terraform configurations** for AWS infrastructure
- **Creates GitHub pull requests** with proper approval workflows
- **Extends existing policies** instead of creating duplicates

## 🎯 **Key Features**

### **Intelligent Request Classification**
- Detects S3 bucket creation requests vs IAM access requests
- Routes to appropriate workflow automatically

### **Smart Policy Management** 
- **Extends existing IAM policies** instead of creating new ones
- Preserves existing permissions while adding new access
- Follows enterprise security best practices

### **Hybrid Interface**
- **Tool Mode**: Process ServiceNow tickets automatically
- **Chat Mode**: Interactive Q&A about company standards

### **GitHub Integration**
- Creates feature branches from `dev` branch
- Generates comprehensive pull requests with security checklists
- Targets `dev` branch for proper review workflow

## 🚀 **Usage**

```bash
# Run the hybrid agent
python main.py

# Process a specific ticket
🛠️ Tool> process ticket_004

# Switch to chat mode  
🛠️ Tool> mode chat

# Ask questions about company standards
💬 Chat> How do I configure S3 encryption?
```

## 📊 **Architecture**

- **Agent Orchestration**: [`agent/core/s3_agent.py`](agent/core/s3_agent.py)
- **Tool Framework**: [`agent/tools/`](agent/tools/)
- **Knowledge Base**: [`data/`](data/)
- **Configuration**: [`agent_config.py`](agent_config.py)

## 🔧 **Setup**

1. Install dependencies: `pip install -r requirements.txt`
2. Configure `.env` with OpenAI API key
3. Optional: Set GitHub token for real PR creation
4. Run: `python main.py`

## 💡 **Business Value**

- **Automation**: Reduces manual infrastructure provisioning time
- **Compliance**: Ensures company standards are followed
- **Security**: Implements least-privilege IAM policies
- **Audit Trail**: Complete workflow documentation
- **Human Oversight**: PR-based approval process

This is the **production-ready agentic system** for enterprise infrastructure automation!

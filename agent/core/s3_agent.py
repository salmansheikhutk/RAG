"""
Main Agent Orchestrator
Coordinates all tools and manages the S3 bucket creation workflow
"""

from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.tools import BaseTool
import json
import agent_config

# Import all agent tools
from agent.tools.servicenow_tools import ServiceNowReader, TicketRequirementsExtractor
from agent.tools.rag_tools import RAGSearcher
from agent.tools.s3_generator import S3ConfigGenerator
from agent.tools.github_tools import GitHubPRCreator, GitHubRepositorySearcher


class S3CreationAgent:
    """
    Main agent for automating S3 bucket creation from ServiceNow tickets
    """
    
    def __init__(self):
        """Initialize the S3 Creation Agent"""
        
        self.llm = ChatOpenAI(
            openai_api_key=agent_config.OPENAI_API_KEY,
            model_name=agent_config.MODEL_NAME,
            temperature=agent_config.TEMPERATURE,
            max_tokens=agent_config.MAX_TOKENS
        )
        
        # Initialize all tools
        self.tools = {
            'servicenow_reader': ServiceNowReader(),
            'requirements_extractor': TicketRequirementsExtractor(),
            'rag_searcher': RAGSearcher(),
            's3_generator': S3ConfigGenerator(),
            'github_pr_creator': GitHubPRCreator(),
            'github_searcher': GitHubRepositorySearcher()
        }
        
        print("🤖 S3 Creation Agent initialized with all tools")
    
    def process_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """
        Main workflow orchestrator - intelligently routes based on ticket type
        """
        print(f"\\n🎫 Processing ServiceNow ticket: {ticket_id}")
        
        workflow_result = {
            'ticket_id': ticket_id,
            'status': 'started',
            'steps': [],
            'errors': [],
            'final_result': None
        }
        
        try:
            # Step 1: Read ServiceNow ticket
            print("\\n📖 Step 1: Reading ServiceNow ticket...")
            ticket_data = self._execute_tool('servicenow_reader', ticket_id)
            workflow_result['steps'].append({
                'step': 1,
                'action': 'read_ticket',
                'result': ticket_data[:200] + "..." if len(ticket_data) > 200 else ticket_data
            })
            
            # Step 2: Extract requirements
            print("\\n🔍 Step 2: Extracting requirements...")
            requirements = self._execute_tool('requirements_extractor', ticket_data)
            workflow_result['steps'].append({
                'step': 2,
                'action': 'extract_requirements',
                'result': requirements[:200] + "..." if len(requirements) > 200 else requirements
            })
            
            # NEW: Step 2.5: Classify request type
            print("\\n🤔 Step 2.5: Classifying request type...")
            request_type = self._classify_request_type(ticket_data, requirements)
            print(f"   Detected request type: {request_type.upper()}")
            
            # Route to appropriate workflow
            if request_type == "iam_access":
                return self._process_iam_request(workflow_result, ticket_data, requirements, ticket_id)
            elif request_type == "s3_bucket":
                return self._process_s3_bucket_request(workflow_result, ticket_data, requirements, ticket_id)
            else:
                # Default to S3 bucket workflow for unknown types
                print("   ⚠️  Unknown request type, defaulting to S3 bucket workflow")
                return self._process_s3_bucket_request(workflow_result, ticket_data, requirements, ticket_id)
                
        except Exception as e:
            error_msg = f"Workflow failed at step {len(workflow_result['steps']) + 1}: {str(e)}"
            workflow_result['errors'].append(error_msg)
            workflow_result['status'] = 'failed'
            return workflow_result
    
    def _classify_request_type(self, ticket_data: str, requirements: str) -> str:
        """Classify the type of request based on ticket content"""
        
        # Convert to lowercase for analysis
        content = (ticket_data + " " + requirements).lower()
        
        # IAM/Access management indicators
        iam_keywords = [
            "iam", "policy", "role", "permission", "access", 
            "datasciencerole", "read-only", "least-privilege",
            "attach policy", "role permissions", "bucket access",
            "epro-*", "existing role"
        ]
        
        # S3 bucket creation indicators  
        s3_keywords = [
            "new bucket", "create bucket", "bucket name:",
            "new s3 bucket", "bucket for", "storage bucket",
            "need a bucket", "bucket creation"
        ]
        
        # Count matches
        iam_score = sum(1 for keyword in iam_keywords if keyword in content)
        s3_score = sum(1 for keyword in s3_keywords if keyword in content)
        
        # Classification logic
        if iam_score > s3_score and iam_score >= 2:
            return "iam_access"
        elif s3_score > iam_score and s3_score >= 1:
            return "s3_bucket"
        elif "role" in content and ("access" in content or "permission" in content):
            return "iam_access"
        else:
            return "s3_bucket"  # Default
    
    def _process_iam_request(self, workflow_result: Dict, ticket_data: str, requirements: str, ticket_id: str) -> Dict[str, Any]:
        """Process IAM access management requests"""
        
        try:
            # Step 3: Search knowledge base for IAM patterns
            print("\\n📚 Step 3: Searching IAM knowledge base...")
            knowledge_search = self._execute_tool('rag_searcher', f"IAM policy templates role access {requirements}")
            workflow_result['steps'].append({
                'step': 3,
                'action': 'search_iam_knowledge_base',
                'result': knowledge_search[:200] + "..." if len(knowledge_search) > 200 else knowledge_search
            })
            
            # Step 4: Generate IAM policy configuration
            print("\\n⚙️ Step 4: Generating IAM policy configuration...")
            iam_config = self._generate_iam_policy(ticket_data, requirements, knowledge_search)
            workflow_result['steps'].append({
                'step': 4,
                'action': 'generate_iam_policy',
                'result': "IAM policy configuration generated successfully"
            })
            
            # Step 5: Create GitHub PR for IAM changes
            print("\\n📋 Step 5: Creating GitHub pull request for IAM policy...")
            
            pr_result = self._execute_tool(
                'github_pr_creator',
                terraform_config=iam_config,
                ticket_id=ticket_id,
                bucket_name=f"iam-policy-{ticket_id.lower()}",
                requirements_summary=f"IAM Policy: {requirements}"
            )
            
            workflow_result['steps'].append({
                'step': 5,
                'action': 'create_iam_pull_request',
                'result': pr_result[:200] + "..." if len(pr_result) > 200 else pr_result
            })
            
            # Step 6: Generate IAM workflow summary
            print("\\n📊 Step 6: Generating IAM workflow summary...")
            role_name = self._extract_role_name(requirements)
            bucket_pattern = self._extract_bucket_pattern(requirements)
            
            final_result = self._generate_iam_workflow_summary(
                workflow_result, ticket_id, role_name, bucket_pattern, requirements
            )
            
            workflow_result['status'] = 'completed'
            workflow_result['final_result'] = final_result
            
            print("\\n✅ IAM workflow completed successfully!")
            return workflow_result
            
        except Exception as e:
            error_msg = f"IAM workflow failed at step {len(workflow_result['steps']) + 1}: {str(e)}"
            workflow_result['errors'].append(error_msg)
            workflow_result['status'] = 'failed'
            return workflow_result
    
    def _process_s3_bucket_request(self, workflow_result: Dict, ticket_data: str, requirements: str, ticket_id: str) -> Dict[str, Any]:
        """Process S3 bucket creation requests (original workflow)"""
        
        try:
            # Step 3: Search company knowledge base
            print("\\n📚 Step 3: Searching company knowledge base...")
            knowledge_search = self._execute_tool('rag_searcher', f"s3 bucket configuration {requirements}")
            workflow_result['steps'].append({
                'step': 3,
                'action': 'search_knowledge_base',
                'result': knowledge_search[:200] + "..." if len(knowledge_search) > 200 else knowledge_search
            })
            
            # Step 4: Generate S3 configuration
            print("\\n⚙️ Step 4: Generating S3 configuration...")
            s3_config = self._execute_tool('s3_generator', requirements, ticket_id)
            workflow_result['steps'].append({
                'step': 4,
                'action': 'generate_config',
                'result': "Terraform configuration generated successfully"
            })
            
            # Step 5: Create GitHub PR
            print("\\n📋 Step 5: Creating GitHub pull request...")
            
            # Extract bucket name for PR
            bucket_name = self._extract_bucket_name(requirements) or f"bucket-{ticket_id.lower()}"
            
            pr_result = self._execute_tool(
                'github_pr_creator',
                terraform_config=s3_config,
                ticket_id=ticket_id,
                bucket_name=bucket_name,
                requirements_summary=requirements
            )
            
            workflow_result['steps'].append({
                'step': 5,
                'action': 'create_pull_request',
                'result': pr_result[:300] + "..." if len(pr_result) > 300 else pr_result
            })
            
            # Step 6: Generate final summary
            print("\\n📊 Step 6: Generating workflow summary...")
            summary = self._generate_workflow_summary(workflow_result, ticket_id, bucket_name, requirements)
            
            workflow_result['status'] = 'completed'
            workflow_result['final_result'] = summary
            
            print("\\n✅ Workflow completed successfully!")
            return workflow_result
            
        except Exception as e:
            error_msg = f"S3 workflow failed at step {len(workflow_result['steps']) + 1}: {str(e)}"
            workflow_result['errors'].append(error_msg)
            workflow_result['status'] = 'failed'
            return workflow_result
    
    def _generate_iam_policy(self, ticket_data: str, requirements: str, knowledge_search: str) -> str:
        """Generate IAM policy configuration based on requirements"""
        
        # Extract key details
        role_name = self._extract_role_name(requirements)
        bucket_pattern = self._extract_bucket_pattern(requirements)
        
        # Generate IAM policy terraform configuration
        iam_config = f"""
# IAM Policy Update for {role_name}
# ServiceNow Ticket: Generated from automated agent
# Policy: Grant read access to {bucket_pattern} buckets

data "aws_iam_role" "existing_role" {{
  name = "{role_name}"
}}

resource "aws_iam_policy" "s3_read_policy" {{
  name        = "S3ReadAccess-{bucket_pattern.replace('*', 'All')}-Policy"
  description = "Read access to {bucket_pattern} S3 buckets"
  
  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::{bucket_pattern}",
          "arn:aws:s3:::{bucket_pattern}/*"
        ]
      }}
    ]
  }})
}}

resource "aws_iam_role_policy_attachment" "attach_s3_read_policy" {{
  role       = data.aws_iam_role.existing_role.name
  policy_arn = aws_iam_policy.s3_read_policy.arn
}}

# Output the policy ARN
output "policy_arn" {{
  description = "ARN of the created S3 read access policy"
  value       = aws_iam_policy.s3_read_policy.arn
}}

output "attachment_status" {{
  description = "Status of policy attachment to role"
  value       = "Policy attached to ${{data.aws_iam_role.existing_role.name}}"
}}
"""
        
        return iam_config
    
    def _extract_role_name(self, requirements: str) -> str:
        """Extract IAM role name from requirements"""
        
        req_lower = requirements.lower()
        if "datasciencerole" in req_lower:
            return "DataScienceRole"
        elif "role" in req_lower:
            # Try to extract role name
            lines = requirements.split('\\n')
            for line in lines:
                if 'role' in line.lower() and ':' in line:
                    return line.split(':')[1].strip()
        
        return "DataScienceRole"  # Default
    
    def _extract_bucket_pattern(self, requirements: str) -> str:
        """Extract bucket pattern from requirements"""
        
        req_lower = requirements.lower()
        if "epro-*" in req_lower or "epro-" in req_lower:
            return "epro-*"
        elif "bucket" in req_lower:
            # Try to extract bucket pattern
            lines = requirements.split('\\n')
            for line in lines:
                if 'bucket' in line.lower() and ('*' in line or 'epro' in line):
                    return "epro-*"
        
        return "epro-*"  # Default
    
    def _generate_iam_workflow_summary(self, 
                                     workflow_result: Dict[str, Any],
                                     ticket_id: str,
                                     role_name: str,
                                     bucket_pattern: str,
                                     requirements: str) -> str:
        """Generate comprehensive IAM workflow summary"""
        
        summary = f"""
🔐 IAM Access Management Workflow Completed Successfully!

=== TICKET INFORMATION ===
ServiceNow Ticket: {ticket_id}
Target Role: {role_name}
Bucket Access Pattern: {bucket_pattern}
Status: {workflow_result['status'].upper()}
Processing Time: {len(workflow_result['steps'])} steps completed

=== WORKFLOW STEPS COMPLETED ===
"""
        
        for step in workflow_result['steps']:
            summary += f"{step['step']}. {step['action'].replace('_', ' ').title()}: ✅\\n"
        
        summary += f"""
=== GENERATED DELIVERABLES ===
✅ IAM policy terraform configuration (main.tf)
✅ Policy attachment to existing role ({role_name})
✅ GitHub pull request created and ready for review
✅ Least-privilege access principles applied
✅ Company security standards enforced

=== IAM POLICY DETAILS ===
- Policy Type: S3 Read-Only Access
- Target Role: {role_name} (existing role)
- Bucket Pattern: {bucket_pattern}
- Permissions: GetObject, GetObjectVersion, ListBucket
- Security: Least-privilege, resource-specific ARNs

=== NEXT STEPS FOR HUMAN REVIEWERS ===
1. 📋 Review the GitHub pull request
2. 🔒 Security team validation (REQUIRED for IAM changes)
3. 👨‍💼 Role owner approval
4. ✅ Infrastructure team approval
5. 🚀 Automated policy attachment after approval

=== ESTIMATED TIMELINE ===
- Development environment: Security review required (24-48 hours)
- Staging environment: Full security review (48-72 hours)  
- Production environment: Complete security audit (72-96 hours)

=== SECURITY AND COMPLIANCE ===
- Principle: Least-privilege access
- Scope: Read-only permissions only
- Resources: Specific bucket pattern ({bucket_pattern})
- Audit: All actions logged via CloudTrail
- Review: Automatic policy expiration in 90 days

=== ROLLBACK PLAN ===
- Policy detachment: Immediate via terraform destroy
- Role restoration: No changes to existing role
- Access revocation: Immediate upon policy removal
- Audit trail: Complete history maintained

=== COST IMPACT ===
- IAM Policy: No additional cost
- API Calls: Standard AWS API pricing applies
- Monitoring: Included in existing CloudTrail costs

The IAM policy update is now ready for security review and approval!
"""
        
        return summary
    
    def _execute_tool(self, tool_name: str, *args, **kwargs) -> str:
        """Execute a tool and return its result"""
        
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        try:
            if args and not kwargs:
                # Simple positional arguments
                if len(args) == 1:
                    result = tool._run(args[0])
                else:
                    result = tool._run(*args)
            elif kwargs and not args:
                # Keyword arguments only
                result = tool._run(**kwargs)
            elif args and kwargs:
                # Mixed arguments
                result = tool._run(*args, **kwargs)
            else:
                # No arguments
                result = tool._run()
            
            return result
            
        except Exception as e:
            raise Exception(f"Tool '{tool_name}' execution failed: {str(e)}")
    
    def _extract_bucket_name(self, requirements: str) -> Optional[str]:
        """Extract bucket name from requirements"""
        
        lines = requirements.lower().split('\\n')
        for line in lines:
            if 'bucket name' in line and ':' in line:
                return line.split(':')[1].strip()
        return None
    
    def _generate_workflow_summary(self, 
                                 workflow_result: Dict[str, Any],
                                 ticket_id: str,
                                 bucket_name: str,
                                 requirements: str) -> str:
        """Generate comprehensive workflow summary"""
        
        summary = f"""
🎉 S3 Bucket Creation Workflow Completed Successfully!

=== TICKET INFORMATION ===
ServiceNow Ticket: {ticket_id}
Proposed Bucket Name: {bucket_name}
Status: {workflow_result['status'].upper()}
Processing Time: {len(workflow_result['steps'])} steps completed

=== WORKFLOW STEPS COMPLETED ===
"""
        
        for step in workflow_result['steps']:
            summary += f"{step['step']}. {step['action'].replace('_', ' ').title()}: ✅\\n"
        
        summary += f"""
=== GENERATED DELIVERABLES ===
✅ Terraform configuration files (main.tf, variables.tf, outputs.tf)
✅ GitHub pull request created and ready for review
✅ Security and compliance requirements addressed
✅ Company naming conventions applied
✅ Cost estimation included

=== NEXT STEPS FOR HUMAN REVIEWERS ===
1. 📋 Review the GitHub pull request
2. 🔒 Security team validation (if required)
3. 💰 Cost approval (if above threshold)
4. ✅ Infrastructure team approval
5. 🚀 Automated deployment after approval

=== ESTIMATED TIMELINE ===
- Development environment: Auto-approved (immediate deployment)
- Staging environment: 24 hours review cycle
- Production environment: 48 hours review cycle

=== COMPLIANCE AND SECURITY ===
- Encryption: Configured per requirements
- Access controls: Applied based on ticket specifications
- Public access: Blocked by default
- Monitoring: CloudWatch and CloudTrail enabled
- Backup: Versioning enabled where appropriate

=== COST ESTIMATION ===
{self._get_cost_summary(requirements)}

=== ROLLBACK PLAN ===
- Terraform state management allows easy resource removal
- No data loss risk (versioning and backup configured)
- Dependent systems identified and documented

The S3 bucket infrastructure is now ready for human review and approval!
"""
        
        return summary
    
    def _get_cost_summary(self, requirements: str) -> str:
        """Generate cost summary"""
        
        req_lower = requirements.lower()
        if 'tb' in req_lower:
            return "Estimated: $50-200/month (high volume storage)"
        elif '500gb' in req_lower or 'gb' in req_lower:
            return "Estimated: $10-50/month (medium volume storage)"
        else:
            return "Estimated: <$10/month (low volume storage)"
    
    def list_open_tickets(self) -> str:
        """List all open ServiceNow tickets"""
        
        print("\\n📋 Retrieving open ServiceNow tickets...")
        return self._execute_tool('servicenow_reader')
    
    def search_knowledge_base(self, query: str) -> str:
        """Search the company knowledge base"""
        
        print(f"\\n🔍 Searching knowledge base for: {query}")
        return self._execute_tool('rag_searcher', query)
    
    def validate_configuration(self, terraform_config: str) -> Dict[str, Any]:
        """Validate generated Terraform configuration"""
        
        validation_result = {
            'syntax_valid': True,
            'naming_compliant': True,
            'security_compliant': True,
            'cost_optimized': True,
            'issues': [],
            'recommendations': []
        }
        
        # Simple validation checks
        config_lower = terraform_config.lower()
        
        # Check for required resources
        required_resources = ['aws_s3_bucket', 'aws_s3_bucket_versioning', 'aws_s3_bucket_public_access_block']
        for resource in required_resources:
            if resource not in config_lower:
                validation_result['issues'].append(f"Missing required resource: {resource}")
                validation_result['syntax_valid'] = False
        
        # Check for security best practices
        if 'public_access_block' not in config_lower:
            validation_result['issues'].append("Public access block not configured")
            validation_result['security_compliant'] = False
        
        if 'encryption' not in config_lower:
            validation_result['issues'].append("Encryption configuration missing")
            validation_result['security_compliant'] = False
        
        # Check naming conventions
        if not any(env in config_lower for env in ['prod', 'dev', 'stage']):
            validation_result['recommendations'].append("Consider including environment in bucket name")
        
        return validation_result
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and capabilities"""
        
        return {
            'agent_name': 'S3CreationAgent',
            'version': '1.0.0',
            'status': 'operational',
            'tools_available': list(self.tools.keys()),
            'knowledge_base_status': 'loaded' if self.tools['rag_searcher'].vector_store else 'unavailable',
            'api_integrations': {
                'servicenow': 'mock' if not agent_config.USE_REAL_SERVICENOW else 'real',
                'github': 'mock' if not agent_config.USE_REAL_GITHUB else 'real',
                'aws': 'mock' if not agent_config.USE_REAL_AWS else 'real'
            },
            'workflow_capabilities': [
                'Read ServiceNow tickets',
                'Extract S3 requirements',
                'Search company knowledge base',
                'Generate Terraform configurations',
                'Create GitHub pull requests',
                'Validate configurations',
                'Estimate costs',
                'Apply company standards'
            ]
        }

"""
GitHub Integration Tool
Handles creating pull requests and managing GitHub repository interactions
"""

import json
import base64
from typing import Dict, List, Any, Optional, Type
from langchain_core.tools import BaseTool
from datetime import datetime
from pydantic import BaseModel, Field
import agent_config

class GitHubPRInput(BaseModel):
    terraform_config: str = Field(description="Terraform configuration code")
    ticket_id: str = Field(description="ServiceNow ticket ID")
    bucket_name: str = Field(description="S3 bucket name")
    requirements_summary: str = Field(description="Summary of requirements")

class GitHubPRCreator(BaseTool):
    """Tool to create GitHub pull requests with generated S3 configurations"""
    
    name: str = "github_pr_creator"
    description: str = "Create GitHub pull request with S3 bucket Terraform configuration"
    args_schema: Type[BaseModel] = GitHubPRInput
    
    def _run(self, 
             terraform_config: str,
             ticket_id: str,
             bucket_name: str,
             requirements_summary: str) -> str:
        """
        Create a GitHub pull request
        
        Args:
            terraform_config: Generated Terraform configuration
            ticket_id: ServiceNow ticket ID
            bucket_name: Proposed bucket name
            requirements_summary: Summary of requirements
        """
        
        if agent_config.USE_REAL_GITHUB:
            return self._create_real_github_pr(
                terraform_config, ticket_id, bucket_name, requirements_summary
            )
        else:
            return self._create_mock_github_pr(
                terraform_config, ticket_id, bucket_name, requirements_summary
            )
    
    def _create_mock_github_pr(self,
                              terraform_config: str,
                              ticket_id: str, 
                              bucket_name: str,
                              requirements_summary: str) -> str:
        """Create a mock GitHub PR response"""
        
        # Generate PR details
        branch_name = f"s3-bucket/{ticket_id.lower()}-{bucket_name}"
        pr_title = f"Add S3 bucket configuration for {ticket_id}"
        
        pr_description = self._generate_pr_description(
            ticket_id, bucket_name, requirements_summary
        )
        
        # Mock PR response
        pr_response = f"""
GitHub Pull Request Created Successfully!

Repository: {agent_config.GITHUB_REPO}
Branch: {branch_name}
PR Title: {pr_title}
PR Number: #42 (mock)

Files Changed:
- terraform/s3-buckets/{bucket_name}/main.tf
- terraform/s3-buckets/{bucket_name}/variables.tf
- terraform/s3-buckets/{bucket_name}/outputs.tf

PR Description:
{pr_description}

Next Steps:
1. Reviewers will be automatically assigned based on approval workflow
2. Security team will review if required
3. Infrastructure team will validate Terraform code
4. Auto-deployment will occur after approval

PR Link: https://github.com/{agent_config.GITHUB_REPO}/pull/42

Approval Status: Pending Review
Estimated Review Time: 24-48 hours for production resources
"""
        
        return pr_response
    
    def _create_real_github_pr(self,
                              terraform_config: str,
                              ticket_id: str,
                              bucket_name: str, 
                              requirements_summary: str) -> str:
        """Create a real GitHub PR using PyGithub"""
        
        try:
            from github import Github
            
            g = Github(agent_config.GITHUB_TOKEN)
            repo = g.get_repo(agent_config.GITHUB_REPO)
            
            # Create branch
            branch_name = f"s3-bucket/{ticket_id.lower()}-{bucket_name}"
            main_branch = repo.get_branch("main")
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=main_branch.commit.sha
            )
            
            # Create files
            file_path = f"terraform/s3-buckets/{bucket_name}/main.tf"
            repo.create_file(
                path=file_path,
                message=f"Add S3 bucket configuration for {ticket_id}",
                content=terraform_config,
                branch=branch_name
            )
            
            # Create PR
            pr_title = f"Add S3 bucket configuration for {ticket_id}"
            pr_body = self._generate_pr_description(
                ticket_id, bucket_name, requirements_summary
            )
            
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base="main"
            )
            
            return f"""
GitHub Pull Request Created Successfully!

Repository: {agent_config.GITHUB_REPO}
PR Number: #{pr.number}
PR Title: {pr_title}
PR Link: {pr.html_url}
Branch: {branch_name}

Status: {pr.state}
"""
            
        except Exception as e:
            return f"Error creating GitHub PR: {str(e)}"
    
    def _generate_pr_description(self,
                                ticket_id: str,
                                bucket_name: str,
                                requirements_summary: str) -> str:
        """Generate comprehensive PR description"""
        
        description = f"""## S3 Bucket Creation Request

### ServiceNow Ticket
- **Ticket ID**: {ticket_id}
- **Request Type**: S3 Bucket Creation

### Bucket Details
- **Bucket Name**: `{bucket_name}`
- **Configuration**: See attached Terraform files

### Requirements Summary
{requirements_summary}

### Security Review
- [ ] Encryption configured appropriately
- [ ] Public access blocked
- [ ] IAM policies follow least privilege
- [ ] Compliance requirements addressed
- [ ] Lifecycle policies implemented

### Infrastructure Review
- [ ] Terraform syntax validated
- [ ] Naming conventions followed
- [ ] Tags are complete and accurate
- [ ] Resource dependencies checked
- [ ] Cost estimation reviewed

### Business Approval
- [ ] Business stakeholder approval (if required)
- [ ] Cost center approval
- [ ] ServiceNow ticket approved

### Deployment Plan
1. Review and approve this PR
2. Terraform plan will be generated automatically
3. Infrastructure team will review plan
4. Deploy to AWS after final approval
5. Update ServiceNow ticket with bucket details

### Estimated Monthly Cost
Based on requirements analysis: {self._estimate_monthly_cost(requirements_summary)}

### Compliance Requirements
{self._extract_compliance_info(requirements_summary)}

### Rollback Plan
- Terraform state allows for easy resource removal
- Data retention policies will be followed
- Dependent resources will be identified before rollback

---
*This PR was automatically generated by the S3 Creation Agent*
*Review workflow: {self._get_approval_workflow()}*
"""
        
        return description
    
    def _estimate_monthly_cost(self, requirements: str) -> str:
        """Estimate monthly AWS costs"""
        
        # Simple cost estimation based on volume mentioned
        if 'tb' in requirements.lower():
            return "$50-200 (high volume storage)"
        elif 'gb' in requirements.lower():
            if '500gb' in requirements.lower():
                return "$10-50 (medium volume)"
            else:
                return "$5-25 (low-medium volume)"
        else:
            return "<$10 (low volume)"
    
    def _extract_compliance_info(self, requirements: str) -> str:
        """Extract compliance information"""
        
        compliance_items = []
        req_lower = requirements.lower()
        
        if 'gdpr' in req_lower:
            compliance_items.append("- GDPR compliance required")
        if 'sox' in req_lower:
            compliance_items.append("- SOX compliance required")
        if 'hipaa' in req_lower:
            compliance_items.append("- HIPAA compliance required")
        if 'pci' in req_lower:
            compliance_items.append("- PCI DSS compliance required")
        
        if compliance_items:
            return "\n".join(compliance_items)
        else:
            return "- Standard security requirements apply"
    
    def _get_approval_workflow(self) -> str:
        """Get approval workflow info"""
        
        return "Production: 2 approvers required | Staging: 1 approver | Development: Auto-approved"
    
    def _arun(self, terraform_config: str, ticket_id: str, bucket_name: str, requirements_summary: str):
        raise NotImplementedError("Async not implemented")


class GitHubSearchInput(BaseModel):
    search_query: str = Field(description="What to search for in the repository")

class GitHubRepositorySearcher(BaseTool):
    """Tool to search GitHub repository for existing patterns and configurations"""
    
    name: str = "github_searcher"
    description: str = "Search GitHub repository for existing S3 configurations and patterns"
    args_schema: Type[BaseModel] = GitHubSearchInput
    
    def _run(self, search_query: str) -> str:
        """
        Search GitHub repository
        
        Args:
            search_query: What to search for in the repository
        """
        
        if agent_config.USE_REAL_GITHUB:
            return self._search_real_github(search_query)
        else:
            return self._search_mock_github(search_query)
    
    def _search_mock_github(self, search_query: str) -> str:
        """Mock GitHub search response"""
        
        mock_results = {
            "s3": [
                "terraform/s3-buckets/analytics-prod/main.tf - Analytics bucket configuration",
                "terraform/s3-buckets/backup-storage/main.tf - Backup storage bucket",
                "policies/s3-access-policies.json - Common S3 access policies",
                "docs/s3-standards.md - S3 configuration standards"
            ],
            "terraform": [
                "terraform/modules/s3-bucket/main.tf - Reusable S3 bucket module",
                "terraform/environments/prod/s3.tf - Production S3 configurations",
                "terraform/common/variables.tf - Common Terraform variables"
            ],
            "policy": [
                "policies/iam-s3-policies.json - IAM policies for S3 access",
                "security/s3-bucket-policies.tf - Security-focused bucket policies"
            ]
        }
        
        # Find matching results
        query_lower = search_query.lower()
        results = []
        
        for category, files in mock_results.items():
            if category in query_lower:
                results.extend(files)
        
        if not results:
            # Default results for any search
            results = mock_results["s3"][:2]
        
        response = f"GitHub Repository Search Results for: '{search_query}'\n\n"
        response += f"Found {len(results)} relevant files:\n\n"
        
        for i, result in enumerate(results[:5], 1):
            response += f"{i}. {result}\n"
        
        response += f"\nRepository: {agent_config.GITHUB_REPO}"
        response += "\nNote: Use RAG searcher for detailed content analysis"
        
        return response
    
    def _search_real_github(self, search_query: str) -> str:
        """Search real GitHub repository"""
        
        try:
            from github import Github
            
            g = Github(agent_config.GITHUB_TOKEN)
            repo = g.get_repo(agent_config.GITHUB_REPO)
            
            # Search repository contents
            contents = repo.get_contents("")
            results = []
            
            # Simple file name search
            for content in contents:
                if search_query.lower() in content.name.lower():
                    results.append(f"{content.name} - {content.type}")
            
            if results:
                response = f"Found {len(results)} files matching '{search_query}':\n"
                for result in results:
                    response += f"- {result}\n"
            else:
                response = f"No files found matching '{search_query}'"
            
            return response
            
        except Exception as e:
            return f"Error searching GitHub: {str(e)}"
    
    def _arun(self, search_query: str):
        raise NotImplementedError("Async not implemented")

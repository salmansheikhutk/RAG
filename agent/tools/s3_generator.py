"""
S3 Configuration Generator Tool
Generates Terraform configurations for S3 buckets based on requirements and company standards
"""

import json
import re
from typing import Dict, List, Any, Optional, Type
from langchain_core.tools import BaseTool
from datetime import datetime
from pydantic import BaseModel, Field
import agent_config

class S3GeneratorInput(BaseModel):
    requirements: str = Field(description="Structured requirements for S3 bucket")
    ticket_id: str = Field(default=None, description="Ticket ID for reference")

class S3ConfigGenerator(BaseTool):
    """Tool to generate S3 bucket Terraform configuration based on requirements"""
    
    name: str = "s3_config_generator"
    description: str = "Generate Terraform configuration for S3 buckets following company standards"
    args_schema: Type[BaseModel] = S3GeneratorInput
    
    def _run(self, requirements: str, ticket_id: str = None) -> str:
        """
        Generate S3 configuration based on requirements
        
        Args:
            requirements: Extracted requirements from ticket
            ticket_id: ServiceNow ticket ID for reference
        """
        
        # Parse requirements (in real system, would use LLM for better parsing)
        parsed_req = self._parse_requirements(requirements)
        
        # Apply company standards and generate config
        config = self._generate_terraform_config(parsed_req, ticket_id)
        
        # Generate supporting files
        variables = self._generate_variables(parsed_req)
        outputs = self._generate_outputs(parsed_req)
        
        response = f"""
Generated S3 Bucket Configuration:

=== main.tf ===
{config}

=== variables.tf ===
{variables}

=== outputs.tf ===
{outputs}

=== Configuration Summary ===
- Bucket Name: {parsed_req.get('bucket_name', 'auto-generated')}
- Environment: {parsed_req.get('environment', 'unknown')}
- Encryption: {parsed_req.get('encryption', 'AES-256')}
- Versioning: {parsed_req.get('versioning', 'Enabled')}
- Estimated Monthly Cost: {parsed_req.get('estimated_cost', 'Unknown')}
- Compliance: {parsed_req.get('compliance', 'Standard')}

=== Next Steps ===
1. Review configuration against requirements
2. Validate naming conventions
3. Create pull request
4. Submit for approval
"""
        
        return response
    
    def _parse_requirements(self, requirements: str) -> Dict[str, Any]:
        """Parse requirements string into structured data"""
        
        req = {}
        lines = requirements.lower().split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if 'bucket name' in key:
                    req['bucket_name'] = value
                elif 'environment' in key:
                    req['environment'] = value
                elif 'encryption' in key:
                    req['encryption'] = value
                elif 'versioning' in key:
                    req['versioning'] = value
                elif 'lifecycle' in key:
                    req['lifecycle'] = value
                elif 'compliance' in key:
                    req['compliance'] = value
                elif 'access' in key:
                    req['access_requirements'] = value
                elif 'cost' in key:
                    req['estimated_cost'] = value
        
        # Apply defaults
        req.setdefault('environment', 'development')
        req.setdefault('encryption', 'AES-256')
        req.setdefault('versioning', 'Enabled')
        req.setdefault('public_access', 'Blocked')
        
        return req
    
    def _generate_terraform_config(self, req: Dict[str, Any], ticket_id: str = None) -> str:
        """Generate main Terraform configuration"""
        
        bucket_name = req.get('bucket_name') or self._generate_bucket_name(req)
        resource_name = re.sub(r'[^a-zA-Z0-9_]', '_', bucket_name)
        
        # Determine encryption configuration
        encryption_config = self._get_encryption_config(req.get('encryption', 'AES-256'))
        
        # Generate lifecycle configuration
        lifecycle_config = self._get_lifecycle_config(req.get('lifecycle', ''))
        
        # Generate tags
        tags = self._generate_tags(req, ticket_id)
        
        config = f'''# S3 Bucket Configuration
# Generated for ServiceNow ticket: {ticket_id or 'N/A'}
# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

resource "aws_s3_bucket" "{resource_name}" {{
  bucket = var.bucket_name != "" ? var.bucket_name : "{bucket_name}"
  
  tags = {json.dumps(tags, indent=4)}
}}

# Versioning Configuration
resource "aws_s3_bucket_versioning" "{resource_name}_versioning" {{
  bucket = aws_s3_bucket.{resource_name}.id
  versioning_configuration {{
    status = "{req.get('versioning', 'Enabled')}"
  }}
}}

# Encryption Configuration
resource "aws_s3_bucket_server_side_encryption_configuration" "{resource_name}_encryption" {{
  bucket = aws_s3_bucket.{resource_name}.id

{encryption_config}
}}

# Public Access Block
resource "aws_s3_bucket_public_access_block" "{resource_name}_pab" {{
  bucket = aws_s3_bucket.{resource_name}.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}}

{lifecycle_config}

# Bucket Policy (if needed)
{self._get_bucket_policy(req, resource_name)}'''

        return config
    
    def _generate_bucket_name(self, req: Dict[str, Any]) -> str:
        """Generate bucket name following company conventions"""
        
        env = req.get('environment', 'dev')[:4]  # Truncate to 4 chars
        purpose = req.get('purpose', 'data')
        service = req.get('service', 'general')
        
        # Follow naming convention: {env}-{service}-{purpose}-{region}
        name = f"{env}-{service}-{purpose}-{agent_config.DEFAULT_REGION}"
        
        # Clean up name
        name = re.sub(r'[^a-z0-9-]', '', name.lower())
        name = re.sub(r'-+', '-', name)  # Remove multiple dashes
        
        return name
    
    def _get_encryption_config(self, encryption_type: str) -> str:
        """Generate encryption configuration block"""
        
        if 'kms' in encryption_type.lower():
            return '''  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_id
    }
    bucket_key_enabled = true
  }'''
        else:
            return '''  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }'''
    
    def _get_lifecycle_config(self, lifecycle_req: str) -> str:
        """Generate lifecycle configuration"""
        
        if not lifecycle_req:
            return ""
        
        # Parse lifecycle requirements
        if 'delete after' in lifecycle_req.lower():
            # Extract number of days/years
            if 'year' in lifecycle_req.lower():
                days = 365 * 7  # Default 7 years
                if '2 year' in lifecycle_req.lower():
                    days = 365 * 2
            elif 'day' in lifecycle_req.lower():
                days = 30  # Default 30 days
            else:
                days = 365  # Default 1 year
            
            return f'''
# Lifecycle Configuration
resource "aws_s3_bucket_lifecycle_configuration" "lifecycle" {{
  bucket = aws_s3_bucket.{re.sub(r'[^a-zA-Z0-9_]', '_', self._generate_bucket_name({}))}.id

  rule {{
    id     = "lifecycle_rule"
    status = "Enabled"

    expiration {{
      days = {days}
    }}

    noncurrent_version_expiration {{
      noncurrent_days = 30
    }}
  }}
}}'''
        
        return ""
    
    def _generate_tags(self, req: Dict[str, Any], ticket_id: str = None) -> Dict[str, str]:
        """Generate tags following company standards"""
        
        tags = agent_config.COMPANY_TAGS.copy()
        
        tags.update({
            "Environment": req.get('environment', 'development'),
            "Purpose": req.get('purpose', 'general-storage'),
            "CreatedDate": datetime.now().strftime('%Y-%m-%d'),
            "CreatedBy": "S3-Creation-Agent"
        })
        
        if ticket_id:
            tags["ServiceNowTicket"] = ticket_id
        
        if req.get('compliance'):
            tags["Compliance"] = req['compliance']
        
        if req.get('cost_center'):
            tags["CostCenter"] = req['cost_center']
        
        return tags
    
    def _get_bucket_policy(self, req: Dict[str, Any], resource_name: str) -> str:
        """Generate bucket policy if needed"""
        
        access_req = req.get('access_requirements', '').lower()
        
        if not access_req or 'none' in access_req:
            return ""
        
        # Generate basic policy template
        return f'''
# Bucket Policy
resource "aws_s3_bucket_policy" "{resource_name}_policy" {{
  bucket = aws_s3_bucket.{resource_name}.id

  policy = jsonencode({{
    Version = "2012-10-17"
    Statement = [
      {{
        Sid    = "RestrictAccess"
        Effect = "Allow"
        Principal = {{
          AWS = var.authorized_principals
        }}
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.{resource_name}.arn,
          "${{aws_s3_bucket.{resource_name}.arn}}/*"
        ]
      }}
    ]
  }})
}}'''
    
    def _generate_variables(self, req: Dict[str, Any]) -> str:
        """Generate variables.tf file"""
        
        return f'''variable "bucket_name" {{
  description = "Name of the S3 bucket"
  type        = string
  default     = "{req.get('bucket_name', '')}"
}}

variable "environment" {{
  description = "Environment (production, staging, development)"
  type        = string
  default     = "{req.get('environment', 'development')}"
}}

variable "kms_key_id" {{
  description = "KMS key ID for encryption"
  type        = string
  default     = null
}}

variable "authorized_principals" {{
  description = "List of authorized AWS principals"
  type        = list(string)
  default     = []
}}

variable "retention_days" {{
  description = "Number of days to retain objects"
  type        = number
  default     = 365
}}'''
    
    def _generate_outputs(self, req: Dict[str, Any]) -> str:
        """Generate outputs.tf file"""
        
        bucket_name = req.get('bucket_name') or self._generate_bucket_name(req)
        resource_name = re.sub(r'[^a-zA-Z0-9_]', '_', bucket_name)
        
        return f'''output "bucket_name" {{
  description = "Name of the created S3 bucket"
  value       = aws_s3_bucket.{resource_name}.id
}}

output "bucket_arn" {{
  description = "ARN of the created S3 bucket"
  value       = aws_s3_bucket.{resource_name}.arn
}}

output "bucket_domain_name" {{
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.{resource_name}.bucket_domain_name
}}

output "bucket_hosted_zone_id" {{
  description = "Route 53 Hosted Zone ID for the S3 bucket"
  value       = aws_s3_bucket.{resource_name}.hosted_zone_id
}}'''
    
    def _arun(self, requirements: str, ticket_id: str = None):
        raise NotImplementedError("Async not implemented")

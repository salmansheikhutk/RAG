# IAM Policy for Data Science Team Access to Enterprise Production Buckets
# This template grants read-only access to epro-* S3 buckets

# Data source to get existing IAM role
data "aws_iam_role" "data_science_role" {
  name = "DataScienceRole"
}

# IAM Policy Document for Enterprise Production Bucket Access
data "aws_iam_policy_document" "data_science_epro_read" {
  statement {
    sid    = "AllowEnterpriseProductionRead"
    effect = "Allow"
    
    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion", 
      "s3:ListBucket",
      "s3:GetBucketLocation",
      "s3:GetBucketVersioning"
    ]
    
    resources = [
      "arn:aws:s3:::epro-*",
      "arn:aws:s3:::epro-*/*"
    ]
    
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["true"]
    }
  }
  
  statement {
    sid    = "AllowListAllBucketsForConsole"
    effect = "Allow"
    
    actions = [
      "s3:ListAllMyBuckets",
      "s3:GetBucketLocation"
    ]
    
    resources = ["*"]
  }
}

# IAM Policy Resource
resource "aws_iam_policy" "data_science_epro_read_policy" {
  name        = "DataScienceEproReadPolicy"
  description = "Read-only access to enterprise production (epro-*) S3 buckets for Data Science team"
  path        = "/"
  
  policy = data.aws_iam_policy_document.data_science_epro_read.json
  
  tags = {
    Name        = "DataScienceEproReadPolicy"
    Environment = "Production"
    Team        = "DataScience"
    Purpose     = "S3ReadAccess"
    CreatedBy   = "S3CreationAgent"
    ManagedBy   = "CloudInfrastructureTeam"
    Compliance  = "LeastPrivilege"
  }
}

# Attach the policy to the existing DataScienceRole
resource "aws_iam_role_policy_attachment" "data_science_epro_read_attachment" {
  role       = data.aws_iam_role.data_science_role.name
  policy_arn = aws_iam_policy.data_science_epro_read_policy.arn
}

# Output the policy ARN for reference
output "data_science_epro_policy_arn" {
  description = "ARN of the DataScienceEproReadPolicy"
  value       = aws_iam_policy.data_science_epro_read_policy.arn
}

output "policy_attachment_id" {
  description = "ID of the policy attachment"
  value       = aws_iam_role_policy_attachment.data_science_epro_read_attachment.id
}

# Variables for customization
variable "data_science_role_name" {
  description = "Name of the existing Data Science IAM role"
  type        = string
  default     = "DataScienceRole"
}

variable "bucket_prefix" {
  description = "S3 bucket prefix pattern for access"
  type        = string
  default     = "epro-"
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

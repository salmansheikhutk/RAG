
# IAM Policy Update for DataScienceRole
# ServiceNow Ticket: Generated from automated agent
# Policy: Grant read access to epro-* buckets

data "aws_iam_role" "existing_role" {
  name = "DataScienceRole"
}

resource "aws_iam_policy" "s3_read_policy" {
  name        = "S3ReadAccess-epro-All-Policy"
  description = "Read access to epro-* S3 buckets"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::epro-*",
          "arn:aws:s3:::epro-*/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_s3_read_policy" {
  role       = data.aws_iam_role.existing_role.name
  policy_arn = aws_iam_policy.s3_read_policy.arn
}

# Output the policy ARN
output "policy_arn" {
  description = "ARN of the created S3 read access policy"
  value       = aws_iam_policy.s3_read_policy.arn
}

output "attachment_status" {
  description = "Status of policy attachment to role"
  value       = "Policy attached to ${data.aws_iam_role.existing_role.name}"
}

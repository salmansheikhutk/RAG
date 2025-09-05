# Standard S3 Bucket Terraform Templates

# Production Data Storage Template
resource "aws_s3_bucket" "production_data" {
  bucket = var.bucket_name

  tags = {
    Name        = var.bucket_display_name
    Environment = "production"
    Owner       = var.owner_team
    Purpose     = var.business_purpose
    CostCenter  = var.cost_center
    Compliance  = var.compliance_requirements
  }
}

resource "aws_s3_bucket_versioning" "production_versioning" {
  bucket = aws_s3_bucket.production_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "production_encryption" {
  bucket = aws_s3_bucket.production_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = var.encryption_type
      kms_master_key_id = var.kms_key_id
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "production_pab" {
  bucket = aws_s3_bucket.production_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Development/Testing Template
resource "aws_s3_bucket" "development_data" {
  bucket = var.bucket_name

  tags = {
    Name        = var.bucket_display_name
    Environment = "development"
    Owner       = var.owner_team
    Purpose     = var.business_purpose
    AutoDelete  = "30-days"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "dev_lifecycle" {
  bucket = aws_s3_bucket.development_data.id

  rule {
    id     = "auto_delete_dev_data"
    status = "Enabled"

    expiration {
      days = 30
    }

    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

# Backup Storage Template
resource "aws_s3_bucket" "backup_storage" {
  bucket = var.bucket_name

  tags = {
    Name        = var.bucket_display_name
    Environment = var.environment
    Owner       = var.owner_team
    Purpose     = "backup-storage"
    Retention   = var.retention_period
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "backup_lifecycle" {
  bucket = aws_s3_bucket.backup_storage.id

  rule {
    id     = "backup_lifecycle_policy"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }

    expiration {
      days = var.retention_days
    }
  }
}

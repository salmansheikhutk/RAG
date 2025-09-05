# Company AWS S3 Naming Conventions

## Bucket Naming Standards

### Format: `{environment}-{service}-{purpose}-{region-code}`

### Environment Prefixes:
- `prod-` : Production resources
- `stage-` : Staging/UAT environment
- `dev-` : Development environment
- `sandbox-` : Temporary/experimental resources

### Service Categories:
- `analytics-` : Data analytics and ML workloads
- `backup-` : Backup and disaster recovery
- `web-` : Web application assets
- `api-` : API-related data
- `etl-` : Data processing pipelines
- `logs-` : Application and system logs
- `artifacts-` : Build and deployment artifacts

### Purpose Indicators:
- `data` : Raw data storage
- `processed` : Processed/transformed data
- `temp` : Temporary storage
- `archive` : Long-term archival
- `static` : Static web assets
- `media` : Images, videos, documents

### Examples:
- `prod-analytics-customer-data-us-east-1`
- `stage-web-static-assets-us-west-2`
- `dev-etl-temp-processing-us-east-1`
- `prod-backup-database-snapshots-us-east-1`

## Tagging Requirements

### Mandatory Tags:
- `Environment` : prod/stage/dev/sandbox
- `Owner` : Team/department responsible
- `Purpose` : Business purpose description
- `CostCenter` : Billing cost center code
- `CreatedBy` : Email of requester
- `CreatedDate` : YYYY-MM-DD format

### Optional Tags:
- `Project` : Project name if applicable
- `Compliance` : GDPR/SOX/HIPAA/PCI if applicable
- `AutoDelete` : Lifecycle policy summary
- `Backup` : Backup requirements
- `Monitoring` : CloudWatch monitoring level

## Compliance Requirements

### GDPR Buckets:
- Must use KMS encryption
- Must have access logging enabled
- Must have lifecycle policies for data retention
- Must have restricted access policies

### SOX Buckets:
- Must enable versioning
- Must have MFA delete enabled
- Must have detailed access logging
- Must have immutable backup copies

### PCI Buckets:
- Must use customer-managed KMS keys
- Must have dedicated IAM policies
- Must have VPC endpoints for access
- Must have real-time monitoring

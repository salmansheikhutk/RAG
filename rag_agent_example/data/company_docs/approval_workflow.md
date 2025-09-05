# Pull Request Approval Workflow

## S3 Infrastructure Changes

### Approval Requirements by Environment:

#### Production Changes:
- **Required Approvers**: 2 approvers minimum
  - 1x Cloud Infrastructure team member
  - 1x Security team member (if security-related)
  - 1x Business stakeholder (for cost impact > $500/month)

#### Staging Changes:
- **Required Approvers**: 1 approver minimum
  - 1x Cloud Infrastructure team member

#### Development Changes:
- **Required Approvers**: Auto-approved for standard patterns
  - Manual review required for non-standard configurations

### PR Content Requirements:

#### Mandatory Information:
- **ServiceNow Ticket**: Link to originating ticket
- **Business Justification**: Why this bucket is needed
- **Cost Estimate**: Monthly cost projection
- **Security Review**: Compliance and access control summary
- **Testing Plan**: How changes will be validated

#### Code Quality Checks:
- Terraform plan output included
- No hardcoded values (use variables)
- Follows naming conventions
- Includes proper tagging
- Security policies attached

### Automated Validations:

#### Before Merge:
- Terraform syntax validation
- Security policy validation
- Cost estimation check
- Naming convention compliance
- Tag completeness verification

#### Post-Merge Actions:
- Automatic infrastructure deployment
- ServiceNow ticket update
- Cost center notification
- Documentation update
- Monitoring setup

## Review Process Timeline:

### Standard Timeline:
- **Development**: Auto-approved or 2 hours
- **Staging**: 24 hours maximum
- **Production**: 48 hours maximum

### Expedited Process:
- **Emergency**: 4 hours (requires C-level approval)
- **Security Issue**: 8 hours (requires security team lead approval)

### Escalation Process:
- Day 1: Automatic reminder to reviewers
- Day 2: Manager notification  
- Day 3: Director escalation
- Day 4: VP approval override available

## Common Review Comments:

### Frequent Issues:
- Missing or incorrect tags
- Overprivileged access policies
- Missing lifecycle policies
- Incorrect naming conventions
- No cost optimization

### Best Practices Reminders:
- Use least privilege access
- Enable appropriate monitoring
- Consider data classification
- Plan for disaster recovery
- Document access patterns

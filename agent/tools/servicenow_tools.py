"""
ServiceNow Integration Tool
Handles reading and processing ServiceNow tickets
"""

import json
import os
from typing import Dict, List, Any, Optional, Type
from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
import agent_config

class ServiceNowReaderInput(BaseModel):
    ticket_number: str = Field(default=None, description="Specific ticket ID to read, or None for all open tickets")

class ServiceNowReader(BaseTool):
    """Tool to read and process ServiceNow tickets for S3 bucket requests"""
    
    name: str = "servicenow_reader"
    description: str = "Read ServiceNow tickets to extract S3 bucket requirements and details"
    args_schema: Type[BaseModel] = ServiceNowReaderInput
    
    def _run(self, ticket_number: str = None) -> str:
        """
        Read ServiceNow ticket(s) and extract requirements
        
        Args:
            ticket_number: Specific ticket ID to read, or None for all open tickets
        """
        
        if agent_config.USE_REAL_SERVICENOW:
            return self._read_real_servicenow_ticket(ticket_number)
        else:
            return self._read_mock_servicenow_ticket(ticket_number)
    
    def _read_mock_servicenow_ticket(self, ticket_number: str = None) -> str:
        """Read mock ServiceNow tickets from local files"""
        
        tickets_path = agent_config.TICKETS_PATH
        
        if ticket_number:
            # Read specific ticket
            ticket_file = os.path.join(tickets_path, f"{ticket_number.lower()}.json")
            if os.path.exists(ticket_file):
                with open(ticket_file, 'r') as f:
                    ticket = json.load(f)
                return self._format_ticket_response(ticket)
            else:
                return f"Ticket {ticket_number} not found in system"
        else:
            # Read all available tickets
            tickets = []
            if os.path.exists(tickets_path):
                for filename in os.listdir(tickets_path):
                    if filename.endswith('.json'):
                        with open(os.path.join(tickets_path, filename), 'r') as f:
                            ticket = json.load(f)
                            tickets.append(ticket)
            
            if tickets:
                result = "Open ServiceNow Tickets:\n\n"
                for ticket in tickets:
                    result += f"- {ticket['ticket_id']}: {ticket['short_description']} "
                    result += f"(Priority: {ticket['priority']}, Status: {ticket['state']})\n"
                return result
            else:
                return "No ServiceNow tickets found"
    
    def _format_ticket_response(self, ticket: Dict) -> str:
        """Format ticket data into readable string"""
        
        response = f"""
ServiceNow Ticket Analysis:

Ticket ID: {ticket['ticket_id']}
Title: {ticket['short_description']}
Status: {ticket['state']} 
Priority: {ticket['priority']}
Urgency: {ticket['urgency']}
Requested by: {ticket['requested_by']}
Business Service: {ticket['business_service']}
Cost Center: {ticket['cost_center']}
Due Date: {ticket['due_date']}

Requirements Extracted:
{ticket['description']}

Tags: {', '.join(ticket.get('tags', []))}
Approval Status: {ticket.get('approval_status', 'Unknown')}
"""
        
        if 'attachments' in ticket:
            response += f"\nAttachments: {', '.join(ticket['attachments'])}"
        
        return response
    
    def _read_real_servicenow_ticket(self, ticket_number: str) -> str:
        """Read from real ServiceNow API (placeholder)"""
        # This would implement real ServiceNow API integration
        return "Real ServiceNow integration not implemented - using mock data"
    
    def _arun(self, ticket_number: str = None):
        raise NotImplementedError("Async not implemented")


class RequirementsExtractorInput(BaseModel):
    ticket_description: str = Field(description="Raw ticket description text")

class TicketRequirementsExtractor(BaseTool):
    """Tool to extract structured requirements from ServiceNow tickets"""
    
    name: str = "requirements_extractor"
    description: str = "Extract and structure S3 bucket requirements from ticket description"
    args_schema: Type[BaseModel] = RequirementsExtractorInput
    
    def _run(self, ticket_description: str) -> str:
        """
        Parse ticket description and extract structured requirements
        
        Args:
            ticket_description: Raw ticket description text
        """
        
        # Simple pattern matching for demo - in real system would use LLM
        requirements = {
            "bucket_name": self._extract_bucket_name(ticket_description),
            "environment": self._extract_environment(ticket_description),
            "access_requirements": self._extract_access_requirements(ticket_description),
            "encryption": self._extract_encryption(ticket_description),
            "versioning": self._extract_versioning(ticket_description),
            "lifecycle": self._extract_lifecycle(ticket_description),
            "compliance": self._extract_compliance(ticket_description),
            "estimated_cost": self._estimate_cost(ticket_description)
        }
        
        # Format as readable response
        response = "Extracted Requirements:\n\n"
        for key, value in requirements.items():
            if value:
                response += f"{key.replace('_', ' ').title()}: {value}\n"
        
        return response
    
    def _extract_bucket_name(self, text: str) -> Optional[str]:
        """Extract bucket name from text"""
        lines = text.lower().split('\n')
        for line in lines:
            if 'bucket name' in line and ':' in line:
                return line.split(':')[1].strip()
        return None
    
    def _extract_environment(self, text: str) -> Optional[str]:
        """Extract environment from text"""
        text_lower = text.lower()
        if 'production' in text_lower:
            return 'production'
        elif 'staging' in text_lower or 'stage' in text_lower:
            return 'staging'
        elif 'development' in text_lower or 'dev' in text_lower:
            return 'development'
        elif 'sandbox' in text_lower:
            return 'sandbox'
        return None
    
    def _extract_access_requirements(self, text: str) -> Optional[str]:
        """Extract access requirements"""
        lines = text.lower().split('\n')
        for line in lines:
            if 'access' in line and ':' in line:
                return line.split(':')[1].strip()
        return None
    
    def _extract_encryption(self, text: str) -> Optional[str]:
        """Extract encryption requirements"""
        text_lower = text.lower()
        if 'kms' in text_lower:
            return 'AWS KMS'
        elif 'aes-256' in text_lower:
            return 'AES-256'
        elif 'encrypt' in text_lower:
            return 'Required'
        return None
    
    def _extract_versioning(self, text: str) -> Optional[str]:
        """Extract versioning requirements"""
        text_lower = text.lower()
        if 'versioning' in text_lower:
            if 'enable' in text_lower or 'required' in text_lower:
                return 'Enabled'
            elif 'disable' in text_lower or 'not' in text_lower:
                return 'Disabled'
        return None
    
    def _extract_lifecycle(self, text: str) -> Optional[str]:
        """Extract lifecycle policy requirements"""
        lines = text.lower().split('\n')
        for line in lines:
            if 'lifecycle' in line or 'delete' in line or 'archive' in line:
                return line.strip()
        return None
    
    def _extract_compliance(self, text: str) -> Optional[str]:
        """Extract compliance requirements"""
        text_lower = text.lower()
        compliance = []
        if 'gdpr' in text_lower:
            compliance.append('GDPR')
        if 'sox' in text_lower:
            compliance.append('SOX')
        if 'hipaa' in text_lower:
            compliance.append('HIPAA')
        if 'pci' in text_lower:
            compliance.append('PCI')
        
        return ', '.join(compliance) if compliance else None
    
    def _estimate_cost(self, text: str) -> Optional[str]:
        """Estimate monthly cost based on volume"""
        # Simple cost estimation based on mentioned data volumes
        text_lower = text.lower()
        if 'tb' in text_lower:
            return "High (>$100/month)"
        elif 'gb' in text_lower:
            return "Medium ($10-100/month)"
        else:
            return "Low (<$10/month)"
    
    def _arun(self, ticket_description: str):
        raise NotImplementedError("Async not implemented")

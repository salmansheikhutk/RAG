"""
S3 Bucket Creation Agent - Main Application
Automated S3 bucket provisioning from ServiceNow tickets using AI agents and RAG
"""

import sys
import json
from typing import Dict, Any
from agent.core.s3_agent import S3CreationAgent


def print_banner():
    """Print application banner"""
    print("=" * 80)
    print("🚀 S3 Bucket Creation Agent")
    print("Automated AWS S3 bucket provisioning from ServiceNow tickets")
    print("Using AI agents with Retrieval-Augmented Generation (RAG)")
    print("=" * 80)


def print_help():
    """Print help information"""
    print("""
Available commands:

TICKET PROCESSING:
  process <ticket_id>     - Process a specific ServiceNow ticket
  list-tickets           - Show all open ServiceNow tickets
  
KNOWLEDGE BASE:
  search <query>         - Search company knowledge base
  validate <config>      - Validate Terraform configuration
  
AGENT MANAGEMENT:
  status                 - Show agent status and capabilities
  help                   - Show this help message
  quit/exit             - Exit the application

EXAMPLES:
  process RITM001234           - Process ticket RITM001234
  search "s3 backup policies"  - Search for backup-related info
  list-tickets                - Show available tickets
""")


def format_json_output(data: Dict[str, Any], indent: int = 2) -> str:
    """Format dictionary as pretty JSON"""
    return json.dumps(data, indent=indent, default=str)


def main():
    """Main application loop"""
    
    print_banner()
    
    # Initialize agent
    print("\\n🤖 Initializing S3 Creation Agent...")
    
    try:
        agent = S3CreationAgent()
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        print("\\nPlease check your configuration and try again.")
        return
    
    print_help()
    
    # Main interaction loop
    while True:
        try:
            user_input = input("\\n🤖 Agent> ").strip()
            
            if not user_input:
                continue
            
            # Parse command
            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            # Handle commands
            if command in ['quit', 'exit', 'q']:
                print("\\n👋 Shutting down S3 Creation Agent. Goodbye!")
                break
            
            elif command == 'help':
                print_help()
                continue
            
            elif command == 'status':
                print("\\n📊 Agent Status:")
                status = agent.get_agent_status()
                print(format_json_output(status))
                continue
            
            elif command == 'process':
                if not args:
                    print("❌ Please specify a ticket ID: process <ticket_id>")
                    continue
                
                ticket_id = args[0].upper()
                print(f"\\n🎫 Processing ticket {ticket_id}...")
                
                try:
                    result = agent.process_ticket(ticket_id)
                    
                    if result['status'] == 'completed':
                        print("\\n" + "="*60)
                        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
                        print("="*60)
                        print(result['final_result'])
                    else:
                        print("\\n" + "="*60)
                        print("❌ WORKFLOW FAILED")
                        print("="*60)
                        print(f"Status: {result['status']}")
                        if result['errors']:
                            print("Errors:")
                            for error in result['errors']:
                                print(f"  - {error}")
                        
                        print("\\nSteps completed:")
                        for step in result['steps']:
                            print(f"  {step['step']}. {step['action'].replace('_', ' ').title()}")
                
                except Exception as e:
                    print(f"❌ Error processing ticket: {str(e)}")
                
                continue
            
            elif command == 'list-tickets':
                print("\\n📋 Retrieving open ServiceNow tickets...")
                
                try:
                    tickets = agent.list_open_tickets()
                    print("\\n" + "="*50)
                    print("📋 OPEN SERVICENOW TICKETS")
                    print("="*50)
                    print(tickets)
                except Exception as e:
                    print(f"❌ Error retrieving tickets: {str(e)}")
                
                continue
            
            elif command == 'search':
                if not args:
                    print("❌ Please specify a search query: search <query>")
                    continue
                
                query = ' '.join(args)
                print(f"\\n🔍 Searching knowledge base for: '{query}'")
                
                try:
                    results = agent.search_knowledge_base(query)
                    print("\\n" + "="*50)
                    print("📚 KNOWLEDGE BASE SEARCH RESULTS")
                    print("="*50)
                    print(results)
                except Exception as e:
                    print(f"❌ Error searching knowledge base: {str(e)}")
                
                continue
            
            elif command == 'validate':
                print("❌ Validation command requires Terraform configuration input")
                print("This feature would be implemented with file upload or paste functionality")
                continue
            
            else:
                print(f"❌ Unknown command: '{command}'")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\\n\\n👋 Interrupted by user. Goodbye!")
            break
        
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            print("Type 'help' for available commands")


def demo_mode():
    """Run demo with predefined scenarios"""
    
    print_banner()
    print("\\n🎯 DEMO MODE: Running predefined scenarios")
    
    agent = S3CreationAgent()
    
    # Demo scenarios
    demo_tickets = ["ticket_001", "ticket_002", "ticket_003"]
    
    for i, ticket_id in enumerate(demo_tickets, 1):
        print(f"\\n{'='*60}")
        print(f"📊 DEMO SCENARIO {i}/3: Processing {ticket_id.upper()}")
        print("="*60)
        
        try:
            result = agent.process_ticket(ticket_id)
            
            if result['status'] == 'completed':
                print("✅ Demo scenario completed successfully!")
                print("\\nWorkflow Summary:")
                for step in result['steps']:
                    print(f"  ✅ {step['action'].replace('_', ' ').title()}")
            else:
                print("❌ Demo scenario failed")
                if result['errors']:
                    for error in result['errors']:
                        print(f"  ❌ {error}")
        
        except Exception as e:
            print(f"❌ Demo scenario error: {str(e)}")
        
        if i < len(demo_tickets):
            input("\\nPress Enter to continue to next scenario...")
    
    print("\\n🎉 Demo completed!")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo_mode()
    else:
        main()

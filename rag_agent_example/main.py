"""
S3 Bucket Creation Agent - Hybrid Application
Tool Mode: Automated S3 bucket provisioning from ServiceNow tickets
Chat Mode: Conversational Q&A using AI agents and RAG
"""

import sys
import json
from typing import Dict, Any
from core.s3_agent import S3CreationAgent
from tools.rag_tools import RAGSearcher
from langchain_openai import ChatOpenAI
import agent_config


class HybridAgent:
    """Hybrid agent supporting both tool mode and chat mode"""
    
    def __init__(self):
        self.agent = S3CreationAgent()
        self.rag_searcher = RAGSearcher()
        self.llm = ChatOpenAI(
            model_name=agent_config.MODEL_NAME,
            temperature=agent_config.TEMPERATURE,
            openai_api_key=agent_config.OPENAI_API_KEY
        )
        self.mode = "tool"  # Default mode
        self.chat_history = []
    
    def switch_mode(self, new_mode: str):
        """Switch between tool and chat modes"""
        if new_mode.lower() in ['tool', 'chat']:
            old_mode = self.mode
            self.mode = new_mode.lower()
            return f"✅ Switched from {old_mode} mode to {self.mode} mode"
        else:
            return "❌ Invalid mode. Use 'tool' or 'chat'"
    
    def handle_chat_message(self, message: str) -> str:
        """Handle conversational Q&A"""
        try:
            # Add to chat history
            self.chat_history.append({"role": "user", "message": message})
            
            # Use RAG to search knowledge base
            search_results = self.rag_searcher._run(message)
            
            # Generate conversational response using LLM
            response = self.generate_chat_response(message, search_results)
            
            # Add response to history
            self.chat_history.append({"role": "assistant", "message": response})
            
            return response
            
        except Exception as e:
            return f"❌ Error processing chat message: {str(e)}"
    
    def generate_chat_response(self, question: str, search_results: str) -> str:
        """Generate conversational response using LLM and RAG results"""
        
        prompt = f"""You are an AWS S3 and cloud infrastructure expert assistant. Answer the user's question using the provided context from the company knowledge base.

Context from Knowledge Base:
{search_results}

User Question: {question}

Instructions:
- Provide helpful, accurate information about AWS S3, cloud infrastructure, and company policies
- Use the context from the knowledge base when relevant
- If the context doesn't contain relevant information, use your general AWS knowledge
- Be conversational and helpful
- Include practical examples when appropriate
- If asked about company-specific policies, reference the knowledge base

Answer:"""

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"I'm having trouble generating a response right now. Here's what I found in the knowledge base:\n\n{search_results}"
    
    def get_current_mode_info(self):
        """Get information about current mode"""
        if self.mode == "tool":
            return {
                "mode": "Tool Mode",
                "description": "Process ServiceNow tickets and automate S3 bucket creation",
                "commands": ["process", "list-tickets", "search", "status", "validate"]
            }
        else:
            return {
                "mode": "Chat Mode", 
                "description": "Conversational Q&A about AWS S3, company policies, and best practices",
                "usage": "Just type your questions naturally"
            }


def print_banner():
    """Print application banner"""
    print("=" * 80)
    print("🚀 Hybrid S3 Agent: Tool Mode + Chat Mode")
    print("Automated S3 bucket provisioning & Conversational Q&A")
    print("Using AI agents with Retrieval-Augmented Generation (RAG)")
    print("=" * 80)


def print_help():
    """Print help information"""
    print("""
Available commands:

MODE SWITCHING:
  mode tool             - Switch to tool mode (ServiceNow ticket processing)
  mode chat             - Switch to chat mode (Q&A conversations)

TOOL MODE COMMANDS:
  process <ticket_id>   - Process a specific ServiceNow ticket
  list-tickets         - Show all open ServiceNow tickets
  search <query>       - Search company knowledge base
  validate <config>    - Validate Terraform configuration
  
CHAT MODE:
  Just type your questions naturally, like:
  "How do I configure S3 encryption?"
  "What are the company naming standards?"
  "Show me examples of lifecycle policies"
  
GENERAL:
  status               - Show agent status and current mode
  help                 - Show this help message
  quit/exit           - Exit the application

EXAMPLES:
  mode chat                        - Switch to conversational mode
  process ticket_001               - Process ticket in tool mode
  search "s3 backup policies"      - Search knowledge base
  How do I set up versioning?      - Ask question in chat mode
""")


def format_json_output(data: Dict[str, Any], indent: int = 2) -> str:
    """Format dictionary as pretty JSON"""
    return json.dumps(data, indent=indent, default=str)


def main():
    """Main application loop"""
    
    print_banner()
    
    # Initialize hybrid agent
    print("\\n🤖 Initializing Hybrid S3 Agent...")
    
    try:
        hybrid_agent = HybridAgent()
        print("✅ Hybrid agent initialized successfully!")
        print(f"🔧 Current mode: {hybrid_agent.mode.upper()}")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        print("\\nPlease check your configuration and try again.")
        return
    
    print_help()
    
    # Main interaction loop
    while True:
        try:
            mode_indicator = "🛠️" if hybrid_agent.mode == "tool" else "💬"
            user_input = input(f"\\n{mode_indicator} {hybrid_agent.mode.title()}> ").strip()
            
            if not user_input:
                continue
            
            # Parse command
            parts = user_input.split()
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            # Handle mode switching
            if command == "mode" and len(args) == 1:
                result = hybrid_agent.switch_mode(args[0])
                print(result)
                continue
            
            # Handle commands based on current mode
            if hybrid_agent.mode == "tool":
                # TOOL MODE COMMANDS
                if command == "process" and len(args) == 1:
                    ticket_id = args[0]
                    print(f"\\n🎫 Processing ServiceNow ticket: {ticket_id}")
                    
                    try:
                        result = hybrid_agent.agent.process_ticket(ticket_id)
                        print("\\n" + "="*60)
                        print("📊 WORKFLOW SUMMARY")
                        print("="*60)
                        
                        # Format the result nicely instead of printing raw dictionary
                        if isinstance(result, dict):
                            if result.get('status') == 'completed':
                                print("✅ Status: COMPLETED")
                                print(f"📋 Ticket ID: {result.get('ticket_id', 'N/A')}")
                                print(f"🔧 Steps Completed: {len(result.get('steps', []))}")
                                
                                if result.get('final_result'):
                                    print("\\n📄 WORKFLOW DETAILS:")
                                    print(result['final_result'])
                                
                                if result.get('steps'):
                                    print("\\n🔍 STEP-BY-STEP BREAKDOWN:")
                                    for step in result['steps']:
                                        action_name = step['action'].replace('_', ' ').title()
                                        print(f"  {step['step']}. {action_name}: ✅")
                                
                            else:
                                print(f"❌ Status: {result.get('status', 'UNKNOWN').upper()}")
                                print(f"📋 Ticket ID: {result.get('ticket_id', 'N/A')}")
                                if result.get('errors'):
                                    print("\\n🚨 ERRORS:")
                                    for error in result['errors']:
                                        print(f"  • {error}")
                        else:
                            print(result)
                        
                    except Exception as e:
                        print(f"❌ Failed to process ticket: {str(e)}")
                        
                elif command == "list-tickets":
                    print("\\n📋 Available ServiceNow Tickets:")
                    try:
                        import os
                        import json
                        tickets_path = "./data/tickets"
                        if os.path.exists(tickets_path):
                            ticket_files = [f for f in os.listdir(tickets_path) if f.endswith('.json')]
                            ticket_files.sort()
                            
                            for filename in ticket_files:
                                ticket_id = filename.replace('.json', '')
                                filepath = os.path.join(tickets_path, filename)
                                try:
                                    with open(filepath, 'r') as f:
                                        ticket_data = json.load(f)
                                        short_desc = ticket_data.get('short_description', 'No description')[:60]
                                        if len(ticket_data.get('short_description', '')) > 60:
                                            short_desc += '...'
                                        print(f"  • {ticket_id}: {short_desc}")
                                except Exception as e:
                                    print(f"  • {ticket_id}: (Error reading ticket)")
                        else:
                            print("  No tickets directory found")
                    except Exception as e:
                        print(f"  Error listing tickets: {str(e)}")
                        # Fallback to hardcoded list
                        tickets = ["ticket_001", "ticket_002", "ticket_003"]
                        for ticket in tickets:
                            print(f"  • {ticket}")
                    
                elif command == "search" and args:
                    query = " ".join(args)
                    print(f"\\n🔍 Searching knowledge base for: '{query}'")
                    
                    try:
                        result = hybrid_agent.rag_searcher._run(query)
                        print("\\n" + result)
                    except Exception as e:
                        print(f"❌ Search failed: {str(e)}")
                        
                elif command == "status":
                    mode_info = hybrid_agent.get_current_mode_info()
                    print("\\n📊 Agent Status:")
                    print(f"Mode: {mode_info['mode']}")
                    print(f"Description: {mode_info['description']}")
                    if 'commands' in mode_info:
                        print(f"Available Commands: {', '.join(mode_info['commands'])}")
                    
                elif command in ["quit", "exit"]:
                    print("\\n👋 Goodbye!")
                    break
                    
                elif command == "help":
                    print_help()
                    
                else:
                    print("❌ Unknown command. Type 'help' for available commands")
                    
            else:
                # CHAT MODE - Natural language processing
                if command in ["quit", "exit"]:
                    print("\\n👋 Goodbye!")
                    break
                    
                elif command == "help":
                    print_help()
                    
                elif command == "status":
                    mode_info = hybrid_agent.get_current_mode_info()
                    print("\\n📊 Agent Status:")
                    print(f"Mode: {mode_info['mode']}")
                    print(f"Description: {mode_info['description']}")
                    print(f"Usage: {mode_info['usage']}")
                    
                else:
                    # Handle as conversational Q&A
                    print("\\n🤔 Let me search the knowledge base and think about that...")
                    
                    try:
                        response = hybrid_agent.handle_chat_message(user_input)
                        print(f"\\n💡 **Answer:**\\n{response}")
                    except Exception as e:
                        print(f"❌ Sorry, I encountered an error: {str(e)}")
        
        except KeyboardInterrupt:
            print("\\n\\n👋 Goodbye!")
            break
        
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")


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
            print(f"❌ Error in demo scenario: {str(e)}")
        
        if i < len(demo_tickets):
            input("\\nPress Enter to continue to next scenario...")
    
    print("\\n🎉 Demo completed!")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo_mode()
    else:
        main()

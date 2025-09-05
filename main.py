"""
Main application for IICS RAG Assistant
Simple command-line interface for asking questions about IICS documentation
"""

import sys
from rag_assistant import IICSRAGAssistant


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🚀 IICS RAG Assistant")
    print("Ask questions about Informatica Intelligent Cloud Services")
    print("=" * 60)


def print_help():
    """Print help information"""
    print("\nAvailable commands:")
    print("  ask <question>  - Ask a question about IICS")
    print("  reload         - Reload the documentation")
    print("  help           - Show this help message")
    print("  quit/exit      - Exit the application")
    print()


def main():
    """Main application loop"""
    print_banner()
    
    # Initialize RAG assistant
    assistant = IICSRAGAssistant()
    
    # Check if we should force reload
    force_reload = "--reload" in sys.argv
    
    print("Initializing RAG system...")
    if not assistant.initialize(force_reload=force_reload):
        print("Failed to initialize. Please check your configuration and try again.")
        return
    
    print_help()
    
    # Main interaction loop
    while True:
        try:
            user_input = input("\n💬 Enter your question (or 'help' for commands): ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            elif user_input.lower() == 'reload':
                print("Reloading documentation...")
                if assistant.initialize(force_reload=True):
                    print("✓ Documentation reloaded successfully")
                else:
                    print("❌ Failed to reload documentation")
                continue
            
            # Process question
            if user_input.lower().startswith('ask '):
                question = user_input[4:].strip()
            else:
                question = user_input
            
            if not question:
                print("Please provide a question to ask.")
                continue
            
            # Get answer
            try:
                result = assistant.ask_question(question)
                
                print("\n" + "=" * 60)
                print("📖 Answer:")
                print(result["answer"])
                
                if result["sources"]:
                    print(f"\n📚 Sources: {', '.join(result['sources'])}")
                
                print("=" * 60)
                
            except Exception as e:
                print(f"❌ Error processing question: {str(e)}")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")


def demo_questions():
    """Run some demo questions"""
    print_banner()
    
    assistant = IICSRAGAssistant()
    if not assistant.initialize():
        print("Failed to initialize RAG assistant")
        return
    
    demo_questions_list = [
        "What is IICS?",
        "How do I create a mapping in IICS?",
        "What are the different types of connections available?",
        "How do I configure a secure agent?",
        "What is the difference between a mapping and a mapping task?"
    ]
    
    print("\n🎯 Running demo questions...\n")
    
    for i, question in enumerate(demo_questions_list, 1):
        print(f"\n--- Demo Question {i}/{len(demo_questions_list)} ---")
        try:
            result = assistant.ask_question(question)
            print(f"Answer: {result['answer'][:200]}...")  # Truncate for demo
            print(f"Sources: {', '.join(result['sources'])}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 50)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo_questions()
    else:
        main()

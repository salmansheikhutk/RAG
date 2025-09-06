"""
Simple RAG Test Script - Test the system with sample questions
"""

from simple_rag import SimpleRAG


def test_simple_rag():
    """Test the Simple RAG system with sample questions"""
    print("="*60)
    print("🧪 Testing Simple RAG System")
    print("="*60)
    
    # Initialize RAG system
    rag = SimpleRAG()
    
    # Load or build knowledge base
    if not rag.load_vector_database():
        print("\n📚 Building knowledge base...")
        rag.build_knowledge_base()
    
    # Test questions
    test_questions = [
        "How do I get the name of all the citizens in Bedrock?",
        "What authentication is required for the API?",
        "What are the rate limits?",
        "How do I create a new citizen?",
        "What is Fred Flintstone's occupation?"
    ]
    
    print("\n" + "="*60)
    print("🤖 Testing Sample Questions")
    print("="*60)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Test {i}: {question}")
        print("-" * 50)
        
        result = rag.ask_question(question)
        
        print(f"📝 Answer: {result['answer']}")
        
        if result.get('sources'):
            print(f"\n📚 Sources ({result['context_used']} chunks):")
            for j, source in enumerate(result['sources'], 1):
                print(f"  {j}. Similarity: {source['similarity']:.3f}")
        
        print("\n" + "="*60)
    
    print("✅ Test completed!")


if __name__ == "__main__":
    test_simple_rag()

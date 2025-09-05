"""
Test script to verify the IICS RAG Assistant setup
"""

import os
import sys
from rag_assistant import IICSRAGAssistant
import config


def test_setup():
    """Test basic setup and configuration"""
    print("🧪 Testing IICS RAG Assistant Setup\n")
    
    # Test 1: Check if all required files exist
    print("1. Checking required files...")
    required_files = [
        config.PDF_PATH,
        ".env"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✓ {file_path}")
        else:
            print(f"   ❌ {file_path} - FILE MISSING!")
            return False
    
    # Test 2: Check API key
    print("\n2. Checking OpenAI API key...")
    try:
        if config.OPENAI_API_KEY and config.OPENAI_API_KEY != "your_openai_api_key_here":
            print("   ✓ OpenAI API key is configured")
        else:
            print("   ❌ OpenAI API key not configured!")
            print("   Please add your API key to the .env file")
            return False
    except Exception as e:
        print(f"   ❌ Error checking API key: {e}")
        return False
    
    # Test 3: Try importing required packages
    print("\n3. Checking required packages...")
    try:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_openai import OpenAIEmbeddings, ChatOpenAI
        from langchain_community.vectorstores import Chroma
        from langchain.chains import RetrievalQA
        print("   ✓ All LangChain packages imported successfully")
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Please run: pip install -r requirements.txt")
        return False
    
    # Test 4: Initialize RAG Assistant (without processing documents)
    print("\n4. Testing RAG Assistant initialization...")
    try:
        assistant = IICSRAGAssistant()
        print("   ✓ RAG Assistant initialized successfully")
    except Exception as e:
        print(f"   ❌ Error initializing RAG Assistant: {e}")
        return False
    
    print("\n🎉 All tests passed! Your setup looks good.")
    print("\nNext steps:")
    print("1. Make sure your PDF file contains IICS documentation")
    print("2. Run: python main.py")
    print("3. Ask questions about IICS!")
    
    return True


def quick_test():
    """Quick test with document processing"""
    print("🚀 Quick Test with Document Processing\n")
    
    assistant = IICSRAGAssistant()
    
    print("Initializing RAG system (this may take a few minutes for first run)...")
    success = assistant.initialize()
    
    if success:
        print("\n✅ RAG system initialized successfully!")
        
        # Try a simple question
        test_question = "What is IICS?"
        print(f"\n🤔 Testing with question: '{test_question}'")
        
        try:
            result = assistant.ask_question(test_question)
            print(f"\n📖 Answer: {result['answer'][:200]}...")
            print(f"📚 Sources: {', '.join(result['sources'])}")
            print("\n✅ Quick test completed successfully!")
        except Exception as e:
            print(f"❌ Error during question processing: {e}")
    else:
        print("❌ Failed to initialize RAG system")


if __name__ == "__main__":
    if "--quick" in sys.argv:
        quick_test()
    else:
        test_setup()

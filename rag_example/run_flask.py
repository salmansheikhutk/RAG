#!/usr/bin/env python3
"""
Run the Flask RAG Application
"""

import subprocess
import sys
import os

def check_requirements():
    """Check if required packages are installed"""
    try:
        import flask
        import openai
        import numpy
        from dotenv import load_dotenv
        print("✅ All required packages found")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("📦 Install requirements with: pip install -r flask_requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found")
        print("📝 Create a .env file with: OPENAI_API_KEY=your_api_key_here")
        return False

def main():
    print("🚀 Starting Flask RAG Application")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    print("🌐 Starting Flask server...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🛑 Press Ctrl+C to stop")
    print("=" * 50)
    
    # Run Flask app
    try:
        from app import app, initialize_rag_system
        
        # Initialize RAG system
        if initialize_rag_system():
            app.run(debug=True, host='0.0.0.0', port=5000)
        else:
            print("❌ Failed to initialize RAG system")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Flask app stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

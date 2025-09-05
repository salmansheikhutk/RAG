#!/usr/bin/env python3
"""
Simple run script for the Document Q&A Web Application
"""

if __name__ == "__main__":
    from app import app
    
    print("🚀 Starting Document Q&A Web Application...")
    print("💻 Open your browser to: http://127.0.0.1:5000")
    print("🛑 Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='127.0.0.1', port=5000)

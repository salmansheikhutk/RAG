"""
Simple RAG System - Built from Scratch
No LangChain dependencies, just basic Python + OpenAI

This system demonstrates RAG fundamentals:
1. Document chunking
2. Embedding generation  
3. Vector similarity search
4. Answer generation
"""

import json
import numpy as np
import os
import re
import math
from typing import List, Dict, Any
from openai import OpenAI
import simple_config as config


class SimpleRAG:
    """Simple RAG system built from scratch"""
    
    def __init__(self):
        """Initialize the simple RAG system"""
        print("🤖 Initializing Simple RAG System...")
        
        # Set up OpenAI client
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        
        # Initialize storage
        self.vector_database = []
        self.is_built = False
        
        print("✅ Simple RAG initialized!")
    
    def load_document(self, file_path: str) -> str:
        """Load and extract text from JSON document"""
        print(f"📄 Loading document: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract text content from JSON
            # Convert JSON to readable text format
            text_content = self._json_to_text(data)
            print(f"✅ Loaded {len(text_content)} characters from {os.path.basename(file_path)}")
            return text_content
            
        except Exception as e:
            print(f"❌ Error loading document: {str(e)}")
            return ""
    
    def _json_to_text(self, data: Any, prefix: str = "") -> str:
        """Convert JSON data to readable text format"""
        text_parts = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                section_header = f"{prefix}{key}:"
                text_parts.append(section_header)
                
                if isinstance(value, (dict, list)):
                    nested_text = self._json_to_text(value, prefix + "  ")
                    text_parts.append(nested_text)
                else:
                    text_parts.append(f"{prefix}  {str(value)}")
                    
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    nested_text = self._json_to_text(item, prefix + "  ")
                    text_parts.append(nested_text)
                else:
                    text_parts.append(f"{prefix}- {str(item)}")
                    
        else:
            text_parts.append(f"{prefix}{str(data)}")
        
        return "\n".join(text_parts)
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Split text into chunks for embedding"""
        print(f"✂️ Chunking text into {config.CHUNK_SIZE} character chunks...")
        
        chunks = []
        chunk_id = 0
        
        # Simple chunking by character count with overlap
        for start in range(0, len(text), config.CHUNK_SIZE - config.CHUNK_OVERLAP):
            end = start + config.CHUNK_SIZE
            chunk_text = text[start:end]
            
            # Skip very small chunks
            if len(chunk_text.strip()) < 50:
                continue
            
            chunk = {
                "id": chunk_id,
                "text": chunk_text.strip(),
                "start_pos": start,
                "end_pos": end,
                "length": len(chunk_text.strip())
            }
            
            chunks.append(chunk)
            chunk_id += 1
        
        print(f"✅ Created {len(chunks)} text chunks")
        return chunks
    
    def generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate embeddings for text chunks using OpenAI API"""
        print(f"🧠 Generating embeddings for {len(chunks)} chunks...")
        
        embedded_chunks = []
        
        for i, chunk in enumerate(chunks):
            try:
                print(f"  Processing chunk {i+1}/{len(chunks)}...")
                
                # Call OpenAI embedding API
                response = self.client.embeddings.create(
                    model=config.EMBEDDING_MODEL,
                    input=chunk["text"]
                )
                
                # Extract embedding vector
                embedding = response.data[0].embedding
                
                # Add embedding to chunk data
                chunk_with_embedding = {
                    **chunk,
                    "embedding": embedding,
                    "embedding_model": config.EMBEDDING_MODEL
                }
                
                embedded_chunks.append(chunk_with_embedding)
                
            except Exception as e:
                print(f"❌ Error generating embedding for chunk {i}: {str(e)}")
                continue
        
        print(f"✅ Generated embeddings for {len(embedded_chunks)} chunks")
        return embedded_chunks
    
    def save_vector_database(self, embedded_chunks: List[Dict[str, Any]]):
        """Save embedded chunks to JSON file (our vector database)"""
        print(f"💾 Saving vector database to {config.VECTOR_DATABASE_FILE}...")
        
        database = {
            "metadata": {
                "total_chunks": len(embedded_chunks),
                "embedding_model": config.EMBEDDING_MODEL,
                "chunk_size": config.CHUNK_SIZE,
                "source_document": config.INPUT_DOCUMENT
            },
            "chunks": embedded_chunks
        }
        
        try:
            with open(config.VECTOR_DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2)
            
            print(f"✅ Vector database saved with {len(embedded_chunks)} chunks")
            
        except Exception as e:
            print(f"❌ Error saving vector database: {str(e)}")
    
    def load_vector_database(self) -> bool:
        """Load existing vector database from JSON file"""
        if not os.path.exists(config.VECTOR_DATABASE_FILE):
            print(f"❌ Vector database not found: {config.VECTOR_DATABASE_FILE}")
            return False
        
        print(f"📚 Loading vector database from {config.VECTOR_DATABASE_FILE}...")
        
        try:
            with open(config.VECTOR_DATABASE_FILE, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            self.vector_database = database["chunks"]
            self.is_built = True
            
            chunk_count = len(self.vector_database)
            print(f"✅ Loaded vector database with {chunk_count} chunks")
            return True
            
        except Exception as e:
            print(f"❌ Error loading vector database: {str(e)}")
            return False
    
    def build_knowledge_base(self):
        """Build the complete knowledge base from scratch"""
        print("🏗️ Building knowledge base from scratch...")
        
        # Step 1: Load document
        text_content = self.load_document(config.INPUT_DOCUMENT)
        if not text_content:
            print("❌ Failed to load document")
            return
        
        # Step 2: Chunk text
        chunks = self.chunk_text(text_content)
        if not chunks:
            print("❌ Failed to create chunks")
            return
        
        # Step 3: Generate embeddings
        embedded_chunks = self.generate_embeddings(chunks)
        if not embedded_chunks:
            print("❌ Failed to generate embeddings")
            return
        
        # Step 4: Save vector database
        self.save_vector_database(embedded_chunks)
        
        # Step 5: Load into memory
        self.vector_database = embedded_chunks
        self.is_built = True
        
        print("🎉 Knowledge base built successfully!")
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        # Convert to numpy arrays
        a = np.array(vec1)
        b = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def search_similar_chunks(self, question: str) -> List[Dict[str, Any]]:
        """Search for similar chunks using cosine similarity"""
        if not self.is_built or not self.vector_database:
            print("❌ Vector database not ready. Please build knowledge base first.")
            return []
        
        print(f"🔍 Searching for chunks similar to: '{question}'")
        
        try:
            # Generate embedding for the question
            response = self.client.embeddings.create(
                model=config.EMBEDDING_MODEL,
                input=question
            )
            question_embedding = response.data[0].embedding
            
            # Calculate similarity with all chunks
            similarities = []
            for chunk in self.vector_database:
                similarity = self.cosine_similarity(question_embedding, chunk["embedding"])
                similarities.append({
                    **chunk,
                    "similarity": similarity
                })
            
            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Return top K results
            top_chunks = similarities[:config.TOP_K_RESULTS]
            
            print(f"📚 Found {len(top_chunks)} relevant chunks:")
            for i, chunk in enumerate(top_chunks):
                print(f"  {i+1}. Similarity: {chunk['similarity']:.3f} | Text: {chunk['text'][:100]}...")
            
            return top_chunks
            
        except Exception as e:
            print(f"❌ Error searching chunks: {str(e)}")
            return []
    
    def generate_answer(self, question: str, relevant_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer using OpenAI GPT with retrieved context"""
        print("💬 Generating answer using GPT-3.5-turbo...")
        
        # Prepare context from relevant chunks
        context_parts = []
        for i, chunk in enumerate(relevant_chunks):
            context_parts.append(f"Context {i+1}:\n{chunk['text']}\n")
        
        context = "\n".join(context_parts)
        
        # Create simple prompt
        prompt = f"""You are a helpful assistant answering questions based on provided context.

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Answer the question using only the information provided in the context above
- If the context doesn't contain enough information, say so clearly
- Be concise and accurate
- Reference which context section(s) you used

ANSWER:"""

        try:
            # Call OpenAI Chat API
            response = self.client.chat.completions.create(
                model=config.GENERATION_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.TEMPERATURE,
                max_tokens=config.MAX_TOKENS
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                "answer": answer,
                "question": question,
                "sources": [
                    {
                        "chunk_id": chunk["id"],
                        "similarity": chunk["similarity"],
                        "text_preview": chunk["text"][:200] + "..."
                    }
                    for chunk in relevant_chunks
                ],
                "context_used": len(relevant_chunks)
            }
            
        except Exception as e:
            print(f"❌ Error generating answer: {str(e)}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "question": question,
                "sources": [],
                "context_used": 0
            }
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Complete RAG pipeline: search + generate"""
        print(f"\n🤔 Question: {question}")
        
        if not self.is_built:
            return {
                "answer": "Knowledge base not ready. Please build it first.",
                "question": question,
                "sources": [],
                "error": "Knowledge base not built"
            }
        
        # Step 1: Search for relevant chunks
        relevant_chunks = self.search_similar_chunks(question)
        
        if not relevant_chunks:
            return {
                "answer": "No relevant information found in the knowledge base.",
                "question": question,
                "sources": [],
                "error": "No relevant chunks found"
            }
        
        # Step 2: Generate answer
        result = self.generate_answer(question, relevant_chunks)
        
        return result


def main():
    """Main function to demonstrate the Simple RAG system"""
    print("="*60)
    print("🚀 Simple RAG System Demo")
    print("="*60)
    
    # Initialize RAG system
    rag = SimpleRAG()
    
    # Try to load existing knowledge base
    if not rag.load_vector_database():
        print("\n📚 No existing knowledge base found. Building new one...")
        rag.build_knowledge_base()
    
    # Interactive Q&A loop
    print("\n" + "="*60)
    print("💬 Ask questions about the Flintstone API!")
    print("Type 'quit' to exit")
    print("="*60)
    
    while True:
        question = input("\n❓ Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not question:
            continue
        
        # Get answer
        result = rag.ask_question(question)
        
        print(f"\n🤖 Answer: {result['answer']}")
        
        if result.get('sources'):
            print(f"\n📄 Sources ({result['context_used']} chunks used):")
            for i, source in enumerate(result['sources'], 1):
                print(f"  {i}. Similarity: {source['similarity']:.3f}")
                print(f"     Preview: {source['text_preview']}")
        
        print("\n" + "-"*60)


if __name__ == "__main__":
    main()

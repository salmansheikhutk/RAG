"""
Technical Document RAG System
Simple document Q&A system for business knowledge base
"""

import os
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader, UnstructuredPDFLoader, UnstructuredMarkdownLoader
import config


class DocumentRAGSystem:
    """Simple RAG system for technical document Q&A"""
    
    def __init__(self):
        """Initialize the document Q&A system"""
        
        print("🤖 Initializing Technical Document Q&A System...")
        
        # Initialize OpenAI models
        self.llm = ChatOpenAI(
            openai_api_key=config.OPENAI_API_KEY,
            model_name=config.MODEL_NAME,
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS
        )
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config.OPENAI_API_KEY
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
        )
        
        # Initialize vector store
        self.vector_store = None
        self.qa_chain = None
        
        print("✅ System initialized successfully!")
    
    def load_documents(self, documents_path: str = None) -> List[Document]:
        """Load documents from the specified directory"""
        
        if documents_path is None:
            documents_path = config.DOCUMENTS_PATH
            
        print(f"📁 Loading documents from: {documents_path}")
        
        if not os.path.exists(documents_path):
            print(f"❌ Documents directory not found: {documents_path}")
            return []
        
        documents = []
        file_count = 0
        
        for root, dirs, files in os.walk(documents_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in config.SUPPORTED_EXTENSIONS:
                    try:
                        doc = self._load_single_document(file_path)
                        if doc:
                            documents.extend(doc)
                            file_count += 1
                            print(f"  ✅ Loaded: {file}")
                    except Exception as e:
                        print(f"  ❌ Failed to load {file}: {str(e)}")
        
        print(f"📄 Successfully loaded {file_count} documents with {len(documents)} chunks")
        return documents
    
    def _load_single_document(self, file_path: str) -> Optional[List[Document]]:
        """Load a single document based on its type"""
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == ".txt" or file_ext == ".md":
                loader = TextLoader(file_path, encoding='utf-8')
            elif file_ext == ".pdf":
                loader = UnstructuredPDFLoader(file_path)
            elif file_ext == ".json":
                # Handle JSON files as text
                loader = TextLoader(file_path, encoding='utf-8')
            else:
                return None
                
            documents = loader.load()
            
            # Add metadata
            for doc in documents:
                doc.metadata['source_file'] = os.path.basename(file_path)
                doc.metadata['file_path'] = file_path
                doc.metadata['file_type'] = file_ext
            
            # Split into chunks
            chunks = self.text_splitter.split_documents(documents)
            return chunks
            
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            return None
    
    def build_knowledge_base(self, documents: List[Document] = None):
        """Build the vector knowledge base from documents"""
        
        if documents is None:
            documents = self.load_documents()
        
        if not documents:
            print("❌ No documents to process")
            return
        
        print("🔄 Building vector knowledge base...")
        
        # Create vector store
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=config.VECTOR_STORE_PATH
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": config.RAG_TOP_K_RESULTS}
            ),
            return_source_documents=config.INCLUDE_SOURCES
        )
        
        print("✅ Knowledge base built successfully!")
    
    def load_existing_knowledge_base(self):
        """Load an existing vector knowledge base"""
        
        if not os.path.exists(config.VECTOR_STORE_PATH):
            print("❌ No existing knowledge base found. Please run build_knowledge_base() first.")
            return False
        
        print("📚 Loading existing knowledge base...")
        
        self.vector_store = Chroma(
            persist_directory=config.VECTOR_STORE_PATH,
            embedding_function=self.embeddings
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": config.RAG_TOP_K_RESULTS}
            ),
            return_source_documents=config.INCLUDE_SOURCES
        )
        
        print("✅ Knowledge base loaded successfully!")
        return True
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """Ask a question and get an AI-powered answer"""
        
        if not self.qa_chain:
            return {
                'answer': "❌ Knowledge base not initialized. Please load documents first.",
                'sources': [],
                'error': "Knowledge base not ready"
            }
        
        print(f"🔍 Searching for: {question}")
        
        try:
            # Get answer from QA chain
            result = self.qa_chain({"query": question})
            
            answer = result.get('result', 'No answer found')
            source_docs = result.get('source_documents', [])
            
            # Format sources
            sources = []
            for i, doc in enumerate(source_docs[:config.MAX_SOURCES_DISPLAY]):
                sources.append({
                    'file': doc.metadata.get('source_file', 'Unknown'),
                    'content_preview': doc.page_content[:200] + "...",
                    'file_type': doc.metadata.get('file_type', 'unknown')
                })
            
            return {
                'answer': answer,
                'sources': sources,
                'question': question,
                'found_documents': len(source_docs)
            }
            
        except Exception as e:
            return {
                'answer': f"❌ Error processing question: {str(e)}",
                'sources': [],
                'error': str(e)
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        
        status = {
            'knowledge_base_ready': self.vector_store is not None,
            'qa_chain_ready': self.qa_chain is not None,
            'documents_path': config.DOCUMENTS_PATH,
            'vector_store_path': config.VECTOR_STORE_PATH,
            'model_name': config.MODEL_NAME
        }
        
        if self.vector_store:
            try:
                # Try to get document count
                collection = self.vector_store._collection
                status['document_count'] = collection.count()
            except:
                status['document_count'] = "Unknown"
        
        return status
    
    def search_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search documents without generating an answer"""
        
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            
            results = []
            for doc in docs:
                results.append({
                    'content': doc.page_content,
                    'source_file': doc.metadata.get('source_file', 'Unknown'),
                    'file_type': doc.metadata.get('file_type', 'unknown'),
                    'relevance': 'High'  # Could add actual similarity scores
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []


def main():
    """Main function for testing the system"""
    
    # Initialize system
    rag_system = DocumentRAGSystem()
    
    # Try to load existing knowledge base
    if not rag_system.load_existing_knowledge_base():
        # Build new knowledge base
        rag_system.build_knowledge_base()
    
    # Interactive Q&A loop
    print("\n" + "="*60)
    print("📚 Technical Document Q&A System Ready!")
    print("="*60)
    print("Ask questions about your technical documents.")
    print("Type 'status' to check system status")
    print("Type 'quit' to exit")
    print()
    
    while True:
        question = input("📋 Question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
            
        if question.lower() == 'status':
            status = rag_system.get_system_status()
            print("\n🔧 System Status:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            print()
            continue
            
        if not question:
            continue
            
        # Get answer
        result = rag_system.ask_question(question)
        
        print(f"\n🤖 Answer:")
        print(result['answer'])
        
        if result.get('sources'):
            print(f"\n📄 Sources ({result['found_documents']} documents found):")
            for i, source in enumerate(result['sources'], 1):
                print(f"  {i}. {source['file']} ({source['file_type']})")
                print(f"     {source['content_preview']}")
        
        print("\n" + "-"*60)


if __name__ == "__main__":
    main()

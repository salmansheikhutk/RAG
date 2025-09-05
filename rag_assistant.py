"""
IICS RAG Assistant - Main implementation using LangChain
"""

import os
from typing import List, Dict, Any
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import config


class IICSRAGAssistant:
    """
    RAG Assistant for IICS Documentation
    """
    
    def __init__(self):
        """Initialize the RAG assistant"""
        self.llm = None
        self.embeddings = None
        self.vector_store = None
        self.qa_chain = None
        self._setup_components()
    
    def _setup_components(self):
        """Setup LangChain components"""
        print("Initializing IICS RAG Assistant...")
        
        # Initialize OpenAI components
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=config.OPENAI_API_KEY,
            model="text-embedding-ada-002"
        )
        
        self.llm = ChatOpenAI(
            openai_api_key=config.OPENAI_API_KEY,
            model_name="gpt-3.5-turbo",
            temperature=config.TEMPERATURE,
            max_tokens=config.MAX_TOKENS
        )
        
        print("✓ OpenAI components initialized")
    
    def load_and_process_documents(self, force_reload: bool = False):
        """
        Load PDF and create vector store
        
        Args:
            force_reload: If True, reload documents even if vector store exists
        """
        
        # Check if vector store already exists
        if os.path.exists(config.VECTOR_STORE_PATH) and not force_reload:
            print("Loading existing vector store...")
            self.vector_store = Chroma(
                persist_directory=config.VECTOR_STORE_PATH,
                embedding_function=self.embeddings
            )
            print("✓ Vector store loaded")
            return
        
        # Load PDF document
        print("Loading IICS documentation PDF...")
        if not os.path.exists(config.PDF_PATH):
            raise FileNotFoundError(f"PDF file not found: {config.PDF_PATH}")
        
        loader = PyPDFLoader(config.PDF_PATH)
        documents = loader.load()
        print(f"✓ Loaded {len(documents)} pages")
        
        # Split documents into chunks
        print("Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"✓ Created {len(chunks)} text chunks")
        
        # Create vector store
        print("Creating embeddings and vector store...")
        self.vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=config.VECTOR_STORE_PATH
        )
        
        # Persist the vector store
        self.vector_store.persist()
        print("✓ Vector store created and saved")
    
    def setup_qa_chain(self):
        """Setup the question-answering chain"""
        if not self.vector_store:
            raise ValueError("Vector store not initialized. Run load_and_process_documents() first.")
        
        # Create custom prompt template
        prompt_template = """
You are an expert IICS (Informatica Intelligent Cloud Services) assistant. Use the following pieces of context from the IICS documentation to answer the question. 

If you don't know the answer based on the provided context, just say that you don't know. Don't make up an answer.

Always provide specific, actionable information when possible, and mention relevant IICS concepts, features, or steps.

Context:
{context}

Question: {question}

Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create retrieval QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}  # Retrieve top 4 most similar chunks
            ),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        print("✓ QA chain initialized")
    
    def ask_question(self, question: str) -> Dict[str, Any]:
        """
        Ask a question about IICS
        
        Args:
            question: The question to ask
            
        Returns:
            Dictionary with answer and source information
        """
        if not self.qa_chain:
            raise ValueError("QA chain not initialized. Run setup_qa_chain() first.")
        
        print(f"\n🤔 Question: {question}")
        print("Searching documentation...")
        
        # Get answer from the QA chain
        result = self.qa_chain({"query": question})
        
        answer = result["result"]
        source_docs = result["source_documents"]
        
        # Extract source information
        sources = []
        for doc in source_docs:
            page_num = doc.metadata.get("page", "Unknown")
            sources.append(f"Page {page_num}")
        
        return {
            "answer": answer,
            "sources": sources,
            "num_sources": len(source_docs)
        }
    
    def initialize(self, force_reload: bool = False):
        """
        Initialize the complete RAG system
        
        Args:
            force_reload: If True, reload documents even if vector store exists
        """
        try:
            self.load_and_process_documents(force_reload=force_reload)
            self.setup_qa_chain()
            print("\n🎉 IICS RAG Assistant is ready!")
            return True
        except Exception as e:
            print(f"❌ Error initializing RAG assistant: {str(e)}")
            return False

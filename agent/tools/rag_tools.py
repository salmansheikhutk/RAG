"""
RAG Search Tool
Handles searching the knowledge base for relevant patterns and standards
"""

import os
import json
from typing import List, Dict, Any, Type
from langchain_core.tools import BaseTool
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from pydantic import BaseModel, Field
import agent_config

class RAGSearchInput(BaseModel):
    query: str = Field(description="Search query for knowledge base")

class RAGSearcher(BaseTool):
    """Tool to search the company knowledge base for S3 patterns and standards"""
    
    name: str = "rag_searcher"
    description: str = "Search company knowledge base for S3 standards, templates, and policies"
    args_schema: Type[BaseModel] = RAGSearchInput
    
    def _run(self, query: str) -> str:
        """Search the knowledge base for relevant information"""
        return self._search_knowledge_base(query)
    
    def _search_knowledge_base(self, query: str) -> str:
        """Search company knowledge base using embeddings"""
        
        # Initialize embeddings if not already done
        embeddings = OpenAIEmbeddings(
            openai_api_key=agent_config.OPENAI_API_KEY,
            model="text-embedding-ada-002"
        )
        
        # Try to load existing vector store or create new one
        vector_store_path = agent_config.CHROMA_DB_PATH
        vector_store = None
        
        try:
            if os.path.exists(vector_store_path):
                vector_store = Chroma(
                    persist_directory=vector_store_path,
                    embedding_function=embeddings
                )
            else:
                # Create new vector store
                vector_store = self._create_vector_store(embeddings)
        except Exception as e:
            # Fallback to simple text search if vector store fails
            return self._simple_text_search(query)
        
        # Search the vector store
        if vector_store:
            try:
                # Perform similarity search
                results = vector_store.similarity_search(
                    query,
                    k=agent_config.RAG_TOP_K_RESULTS
                )
                
                if results:
                    response = f"Found {len(results)} relevant documents:\n\n"
                    for i, doc in enumerate(results, 1):
                        response += f"Document {i}:\n{doc.page_content}\n\n"
                    return response
                else:
                    return self._simple_text_search(query)
                    
            except Exception as e:
                return self._simple_text_search(query)
        else:
            return self._simple_text_search(query)
    
    def _create_vector_store(self, embeddings):
        """Create a new vector store from company documents"""
        
        documents = []
        
        # Load tickets
        tickets_path = agent_config.TICKETS_PATH
        if os.path.exists(tickets_path):
            for filename in os.listdir(tickets_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(tickets_path, filename)
                    with open(filepath, 'r') as f:
                        ticket_data = json.load(f)
                        content = f"""
ServiceNow Ticket: {ticket_data['ticket_id']}
Title: {ticket_data['short_description']}
Description: {ticket_data['description']}
Environment: {ticket_data.get('business_service', '')}
Tags: {', '.join(ticket_data.get('tags', []))}
"""
                        doc = Document(
                            page_content=content,
                            metadata={
                                'source': filepath,
                                'type': 'ticket',
                                'ticket_id': ticket_data['ticket_id']
                            }
                        )
                        documents.append(doc)
        
        # Load repository patterns
        repo_path = agent_config.REPO_PATTERNS_PATH
        if os.path.exists(repo_path):
            loader = DirectoryLoader(
                repo_path,
                glob="**/*",
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'}
            )
            repo_docs = loader.load()
            for doc in repo_docs:
                doc.metadata['type'] = 'repo_pattern'
            documents.extend(repo_docs)
        
        # Load company docs
        company_path = agent_config.COMPANY_DOCS_PATH
        if os.path.exists(company_path):
            loader = DirectoryLoader(
                company_path,
                glob="**/*.md",
                loader_cls=TextLoader,
                loader_kwargs={'encoding': 'utf-8'}
            )
            company_docs = loader.load()
            for doc in company_docs:
                doc.metadata['type'] = 'company_standard'
            documents.extend(company_docs)
        
        if documents:
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=agent_config.CHUNK_SIZE,
                chunk_overlap=agent_config.CHUNK_OVERLAP
            )
            chunks = text_splitter.split_documents(documents)
            
            # Create vector store
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=agent_config.CHROMA_DB_PATH
            )
            vector_store.persist()
            return vector_store
        else:
            return None
    
    def _simple_text_search(self, query: str) -> str:
        """Fallback text search when vector search is not available"""
        
        query_lower = query.lower()
        results = []
        
        # Search in tickets
        tickets_path = agent_config.TICKETS_PATH
        if os.path.exists(tickets_path):
            for filename in os.listdir(tickets_path):
                if filename.endswith('.json'):
                    filepath = os.path.join(tickets_path, filename)
                    try:
                        with open(filepath, 'r') as f:
                            ticket_data = json.load(f)
                            content = f"{ticket_data.get('short_description', '')} {ticket_data.get('description', '')}".lower()
                            if any(word in content for word in query_lower.split()):
                                results.append(f"Ticket {ticket_data['ticket_id']}: {ticket_data['short_description']}")
                    except Exception:
                        continue
        
        # Search in repo patterns
        repo_path = agent_config.REPO_PATTERNS_PATH
        if os.path.exists(repo_path):
            for filename in os.listdir(repo_path):
                if filename.endswith(('.tf', '.json')):
                    if any(word in filename.lower() for word in query_lower.split()):
                        results.append(f"Template: {filename}")
        
        # Search in company docs
        company_path = agent_config.COMPANY_DOCS_PATH
        if os.path.exists(company_path):
            for filename in os.listdir(company_path):
                if filename.endswith('.md'):
                    if any(word in filename.lower() for word in query_lower.split()):
                        results.append(f"Policy: {filename}")
        
        if results:
            return f"Found relevant information:\n" + "\n".join(f"- {result}" for result in results[:5])
        else:
            return f"No specific information found for '{query}'. Using standard S3 best practices."
    
    def search_terraform_patterns(self, requirements: str) -> str:
        """Search for relevant Terraform patterns"""
        return self._search_knowledge_base(f"terraform s3 bucket {requirements}")
    
    def search_iam_policies(self, access_type: str) -> str:
        """Search for relevant IAM policies"""
        return self._search_knowledge_base(f"iam policy s3 {access_type}")
    
    def search_naming_standards(self, environment: str, purpose: str) -> str:
        """Search for naming conventions"""
        return self._search_knowledge_base(f"naming convention {environment} {purpose}")
    
    def search_compliance_requirements(self, compliance_type: str) -> str:
        """Search for compliance requirements"""
        return self._search_knowledge_base(f"compliance {compliance_type} requirements")
    
    def _arun(self, query: str):
        raise NotImplementedError("Async not implemented")

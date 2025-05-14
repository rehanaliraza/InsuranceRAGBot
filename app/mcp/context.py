"""
MCP Context - Defines the Context components of the Model-Context-Protocol architecture
"""
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from app.utils.vectorstore import get_relevant_documents, load_vectorstore

class ContextManager:
    """
    Manages context for LLM interactions including retrieving relevant documents, 
    managing conversation history, and preparing context for different agent types
    """
    def __init__(self):
        self._conversation_history = []
        self._vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize the vectorstore"""
        try:
            self._vectorstore = load_vectorstore()
        except Exception as e:
            print(f"Error initializing vectorstore: {e}")
    
    def add_interaction(self, query: str, agent_type: str, response: str):
        """Add an interaction to the conversation history"""
        self._conversation_history.append({
            "query": query,
            "agent_type": agent_type,
            "response": response
        })
    
    def get_relevant_documents(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve relevant documents for a query"""
        return get_relevant_documents(query, self._vectorstore, k=k)
    
    def format_documents(self, docs: List[Document]) -> str:
        """Format documents into a string"""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def get_conversation_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        return self._conversation_history[-limit:] if limit else self._conversation_history
    
    def format_history(self, limit: int = 5) -> str:
        """Format conversation history as a string"""
        history = self.get_conversation_history(limit)
        formatted = []
        
        for interaction in history:
            formatted.append(f"User: {interaction['query']}")
            formatted.append(f"{interaction['agent_type']}: {interaction['response']}")
            
        return "\n".join(formatted)
    
    def get_context_for_agent(self, query: str, agent_type: str, include_history: bool = True) -> Dict[str, Any]:
        """
        Prepare full context for an agent, including relevant documents and conversation history
        """
        # Get relevant documents
        docs = self.get_relevant_documents(query)
        doc_context = self.format_documents(docs)
        
        # Prepare context dictionary
        context = {
            "query": query,
            "documents": doc_context,
            "agent_type": agent_type,
        }
        
        # Add conversation history if requested
        if include_history and self._conversation_history:
            context["history"] = self.format_history()
        
        return context 
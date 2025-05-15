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
        """
        Add a user query and agent response to the conversation history as separate entries
        """
        # First, add the user query
        self._conversation_history.append({
            "content": query,
            "is_user": True,
            "timestamp": import_time()
        })
        
        # Then, add the agent response
        self._conversation_history.append({
            "content": response,
            "agent_type": agent_type,
            "is_user": False,
            "timestamp": import_time()
        })
    
    def get_relevant_documents(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve relevant documents for a query"""
        return get_relevant_documents(query, self._vectorstore, k=k)
    
    def format_documents(self, docs: List[Document]) -> str:
        """Format documents into a string"""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def get_conversation_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        return self._conversation_history[-limit*2:] if limit and self._conversation_history else []
    
    def get_user_queries(self, limit: int = 5) -> List[str]:
        """
        Get just the user queries from the conversation history
        """
        # Filter to just user messages
        user_messages = [item for item in self._conversation_history if item.get("is_user", False)]
        
        # Return the most recent ones, limited by the limit parameter
        return [msg["content"] for msg in user_messages[-limit:]]
    
    def format_history(self, limit: int = 5) -> str:
        """
        Format conversation history as a string with clear distinction between user queries and agent responses
        """
        history = self.get_conversation_history(limit*2)  # Double the limit to get pairs of messages
        if not history:
            return ""
            
        formatted = []
        
        for item in history:
            if item.get("is_user", False):
                formatted.append(f"User: {item['content']}")
            else:
                agent_name = item.get('agent_type', 'Assistant').capitalize()
                formatted.append(f"{agent_name}: {item['content']}")
            
        return "\n\n".join(formatted)
    
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

def import_time():
    """Helper function to get current time"""
    from datetime import datetime
    return datetime.now().isoformat() 
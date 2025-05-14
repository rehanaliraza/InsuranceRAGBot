"""
MCP Executor - The central coordinator that integrates Models, Context, and Protocol
"""
from typing import Dict, Any, Optional, List
from app.mcp.models import ModelProvider
from app.mcp.context import ContextManager
from app.mcp.protocol import PromptProtocol, OutputProtocol, AgentType
import logging

class MCPExecutor:
    """
    The Model-Context-Protocol Executor coordinates the three components:
    - Models: Language models for different agent types
    - Context: Management of documents, history, and other contextual information
    - Protocol: Standardized prompts and output parsing
    """
    def __init__(self):
        self.model_provider = ModelProvider()
        self.context_manager = ContextManager()
        self.prompt_protocol = PromptProtocol()
        self.output_protocol = OutputProtocol()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("MCPExecutor")
    
    def route_query(self, query: str) -> str:
        """
        Determine which agent type should handle the query
        """
        self.logger.info(f"Routing query: {query}")
        
        # Get router model
        router_model = self.model_provider.get_model(AgentType.ROUTER.value)
        
        # Get router prompt
        router_prompt = self.prompt_protocol.get_prompt(AgentType.ROUTER.value)
        
        # Execute routing - fix the chaining syntax
        chain = router_prompt | router_model | self.output_protocol._default_parser
        agent_type = chain.invoke({"query": query}).strip().lower()
        
        # Validate agent type
        if agent_type not in [e.value for e in AgentType]:
            self.logger.warning(f"Invalid agent type '{agent_type}' from router, defaulting to writer")
            agent_type = AgentType.WRITER.value
        
        self.logger.info(f"Routed to agent type: {agent_type}")
        return agent_type
    
    def execute_query(self, query: str, agent_type: Optional[str] = None, include_history: bool = True) -> Dict[str, Any]:
        """
        Execute a query using the MCP architecture
        """
        # Route query if agent_type not specified
        if not agent_type:
            agent_type = self.route_query(query)
        
        self.logger.info(f"Executing query with agent type: {agent_type}")
        
        # Get model for agent type
        model = self.model_provider.get_model(agent_type)
        
        # Get context
        context = self.context_manager.get_context_for_agent(
            query=query,
            agent_type=agent_type,
            include_history=include_history
        )
        
        # Get prompt
        prompt = self.prompt_protocol.get_prompt(agent_type)
        
        # Format variables
        variables = self.prompt_protocol.format_prompt_variables(context)
        
        # Execute query - fix the chaining syntax
        self.logger.info(f"Running model with {len(variables['documents'])} chars of document context")
        chain = prompt | model | self.output_protocol._default_parser
        response = chain.invoke(variables)
        
        # Store in context
        self.context_manager.add_interaction(query, agent_type, response)
        
        # Return results
        return {
            "agent": agent_type,
            "response": response
        }
    
    def execute_with_review(self, query: str) -> Dict[str, Any]:
        """
        Execute a query and then review the result with the tester agent
        """
        # First, execute with primary agent
        primary_result = self.execute_query(query)
        primary_agent = primary_result["agent"]
        primary_response = primary_result["response"]
        
        self.logger.info(f"Reviewing response from {primary_agent}")
        
        # Create verification query
        verification_query = f"Question: {query}\n\nProposed answer: {primary_response}\n\nIs this answer accurate?"
        
        # Execute with tester agent
        tester_result = self.execute_query(
            query=verification_query,
            agent_type=AgentType.TESTER.value,
            include_history=False  # Don't include history for validation
        )
        
        validation = tester_result["response"]
        
        # Return combined results
        return {
            "primary_agent": primary_agent,
            "response": primary_response,
            "validation": validation
        } 
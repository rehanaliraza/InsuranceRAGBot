"""
MCP Executor - The central coordinator that integrates Models, Context, and Protocol
"""
from typing import Dict, Any, Optional, List
from app.mcp.models import ModelProvider
from app.mcp.context import ContextManager
from app.mcp.protocol import PromptProtocol, OutputProtocol, AgentType
from app.utils.metrics import MetricsTracker
import logging
import re
import time
import uuid

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
        
        # Common follow-up questions to append if needed
        self.follow_up_questions = [
            "May I ask what specific aspects of this topic are most important to you?",
            "Have you considered how this might impact your understanding?",
            "Would you like to know about different approaches to this topic?",
            "Is there a particular area of this topic you'd like to explore further?",
            "Do you feel your current knowledge on this topic is sufficient for your needs?",
            "Have you explored other aspects of this topic before?",
            "What interests you most about this particular subject?",
            "Would you like me to provide more details about any specific part?"
        ]
        
        # Meta query patterns for conversation history
        self.history_query_patterns = [
            r"what (did|were) (I|me|my) (say|ask|questions?|prompts?|queries?)",
            r"(show|tell|give) me (the|my|our) (conversation|chat|message|history)",
            r"what (was|were) my (previous|last|prior|earlier) (message|question|prompt|query)",
            r"(can you )?(repeat|list|recap) (what I (said|asked)|my (questions|queries|messages))",
            r"what have I (asked|said) (so far|before)",
        ]
    
    # This method has been removed as part of making the bot more general-purpose
    
    def ensure_follow_up_question(self, response: str, agent_type: str) -> str:
        """
        Ensure the response ends with a follow-up question
        """
        # Check if response already contains a question at the end
        last_paragraph = response.split('\n\n')[-1] if '\n\n' in response else response
        last_sentences = re.split(r'(?<=[.!])\s+', last_paragraph)
        last_sentence = last_sentences[-1] if last_sentences else ""
        
        # If the last sentence already contains a question mark, assume it's a follow-up question
        if '?' in last_sentence:
            return response
            
        # If no question is present, add an appropriate follow-up from our list
        import random
        follow_up = random.choice(self.follow_up_questions)
        
        # Append the follow-up question, ensuring proper formatting
        if response.endswith('.') or response.endswith('!'):
            response += f" {follow_up}"
        else:
            response += f". {follow_up}"
            
        self.logger.info(f"Added follow-up question to {agent_type} response")
        return response
    
    def is_history_query(self, query: str) -> bool:
        """
        Check if the query is asking about conversation history
        """
        query_lower = query.lower()
        
        # Check for direct keywords
        if any(keyword in query_lower for keyword in ["last prompt", "previous prompt", "last question", 
                                                   "previous message", "chat history", "conversation history",
                                                   "what did i ask", "what did i say"]):
            return True
        
        # Check for regex patterns
        for pattern in self.history_query_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True
                
        return False
    
    def format_user_queries(self, limit: int = 5) -> str:
        """
        Format just the user queries from history
        """
        user_queries = self.context_manager.get_user_queries(limit)
        
        if not user_queries:
            return "You haven't asked any questions yet."
            
        formatted_queries = [f"{i+1}. \"{query}\"" for i, query in enumerate(user_queries)]
        return "\n".join(formatted_queries)
    
    def route_query(self, query: str) -> str:
        """
        Determine which agent type should handle the query
        """
        self.logger.info(f"Routing query: {query}")
        
        # Use standard routing
        router_prompt = self.prompt_protocol.get_prompt(AgentType.ROUTER.value)
        router_model = self.model_provider.get_model(AgentType.ROUTER.value)
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
        # Generate a unique query ID for tracking metrics
        query_id = f"query_{uuid.uuid4().hex[:8]}"
        
        # Start tracking total latency
        start_time = time.time()
        
        # Check if the query is asking about conversation history
        if self.is_history_query(query):
            self.logger.info("Detected history query, providing conversation history")
            history = self.format_user_queries(limit=10)
            response = f"Here are your previous questions:\n\n{history}"
            
            # Track latency for system response
            total_latency = time.time() - start_time
            MetricsTracker.track_latency("system_response", "system", total_latency, query_id)
            
            # Add to conversation history (even for history queries)
            self.context_manager.add_interaction(query, "system", response)
            
            # Don't append a follow-up question for meta-queries
            return {
                "agent": "system",
                "response": response
            }
        
        # Route query if agent_type not specified
        if not agent_type:
            routing_start = time.time()
            agent_type = self.route_query(query)
            routing_latency = time.time() - routing_start
            
            # Track routing latency
            MetricsTracker.track_latency("routing", agent_type, routing_latency, query_id)
            MetricsTracker.track_agent_usage(agent_type, "routed", query_id)
        else:
            # Track direct agent usage
            MetricsTracker.track_agent_usage(agent_type, "direct", query_id)
        
        self.logger.info(f"Executing query with agent type: {agent_type}")
        
        # Get model for agent type
        model = self.model_provider.get_model(agent_type)
        
        # Track retrieval metrics and latency
        retrieval_start = time.time()
        
        # Get context
        context = self.context_manager.get_context_for_agent(
            query=query,
            agent_type=agent_type,
            include_history=include_history
        )
        
        # Track retrieval latency
        retrieval_latency = time.time() - retrieval_start
        MetricsTracker.track_latency("retrieval", agent_type, retrieval_latency, query_id)
        
        # Track retrieval metrics if documents were retrieved
        if "documents" in context and context["documents"]:
            # Count the number of documents by splitting on double newlines
            doc_count = len(context["documents"].split("\n\n"))
            MetricsTracker.track_retrieval_metrics(query, doc_count, query_id=query_id)
        
        # Get prompt for agent type
        prompt = self.prompt_protocol.get_prompt(agent_type)
        
        # Execute chain
        llm_start = time.time()
        
        # Format the variables properly
        formatted_context = self.prompt_protocol.format_prompt_variables(context)
        
        chain = prompt | model | self.output_protocol._default_parser
        
        try:
            # Use the properly formatted context
            response = chain.invoke(formatted_context)
            
            # Track LLM latency
            llm_latency = time.time() - llm_start
            MetricsTracker.track_latency("llm_response", agent_type, llm_latency, query_id)
            
            # Estimate token usage (simple estimation)
            prompt_tokens = len(str(context)) // 3  # Rough estimate: 3 chars per token
            completion_tokens = len(response) // 3  # Rough estimate
            
            # Track token usage
            model_name = self.model_provider.get_model_name(agent_type)
            MetricsTracker.track_token_usage(
                agent_type, 
                prompt_tokens, 
                completion_tokens, 
                model_name,
                query_id
            )
            
            # Add sales-oriented follow-up questions if needed
            response = self.ensure_follow_up_question(response, agent_type)
        
            # IMPORTANT: Add to conversation history BEFORE the next query
            # This ensures history is available for the next query
            self.context_manager.add_interaction(query, agent_type, response)
            
            # Track total latency
            total_latency = time.time() - start_time
            MetricsTracker.track_latency("total", agent_type, total_latency, query_id)
            
            return {
                "agent": agent_type,
                "response": response,
                "metrics": {
                    "query_id": query_id,
                    "total_latency": total_latency,
                    "llm_latency": llm_latency,
                    "retrieval_latency": retrieval_latency
                }
            }
        except Exception as e:
            self.logger.error(f"Error executing query: {str(e)}", exc_info=True)
            
            # Track error
            error_latency = time.time() - start_time
            MetricsTracker.track_latency("error", agent_type, error_latency, query_id)
            
            # Return error response
            return {
                "agent": agent_type,
                "response": f"I apologize, but I encountered an error while processing your query. Please try again or rephrase your question."
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
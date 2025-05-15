"""
MCP Executor - The central coordinator that integrates Models, Context, and Protocol
"""
from typing import Dict, Any, Optional, List
from app.mcp.models import ModelProvider
from app.mcp.context import ContextManager
from app.mcp.protocol import PromptProtocol, OutputProtocol, AgentType
import logging
import re

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
        
        # Keywords that suggest sales opportunities
        self.sales_trigger_keywords = [
            "recommend", "suggestion", "best for me", "best option", "should i get",
            "need coverage", "looking for", "shopping", "compare", "difference between",
            "better", "saving", "discount", "price", "cost", "afford", "expensive", "cheap",
            "family", "children", "mortgage", "house", "car", "vehicle", "health", "retirement",
            "plan", "policy", "coverage", "protect", "risk", "worried about"
        ]
        
        # Common sales-oriented follow-up questions to append if needed
        self.sales_follow_up_questions = [
            "May I ask if you currently have any insurance coverage for this situation?",
            "Have you considered how this might affect your long-term financial security?",
            "Would you like to know about options that could provide better protection in this area?",
            "Has your family situation changed recently in ways that might affect your insurance needs?",
            "Do you feel your current coverage is adequate for your specific needs?",
            "Have you reviewed your insurance coverage in the last year?",
            "What concerns you most about your current insurance protection?",
            "Would you be interested in learning how others in similar situations have addressed this?"
        ]
        
        # Meta query patterns for conversation history
        self.history_query_patterns = [
            r"what (did|were) (I|me|my) (say|ask|questions?|prompts?|queries?)",
            r"(show|tell|give) me (the|my|our) (conversation|chat|message|history)",
            r"what (was|were) my (previous|last|prior|earlier) (message|question|prompt|query)",
            r"(can you )?(repeat|list|recap) (what I (said|asked)|my (questions|queries|messages))",
            r"what have I (asked|said) (so far|before)",
        ]
    
    def detect_sales_keywords(self, query: str) -> bool:
        """
        Check if the query contains keywords that suggest sales potential
        """
        query_lower = query.lower()
        for keyword in self.sales_trigger_keywords:
            if keyword in query_lower:
                self.logger.info(f"Sales keyword detected: '{keyword}'")
                return True
        return False
    
    def ensure_follow_up_question(self, response: str, agent_type: str) -> str:
        """
        Ensure the response ends with a follow-up question that could lead to sales
        """
        # If this is already the sales agent, don't modify the response
        if agent_type == AgentType.SALES.value:
            return response
            
        # Check if response already contains a question at the end
        last_paragraph = response.split('\n\n')[-1] if '\n\n' in response else response
        last_sentences = re.split(r'(?<=[.!])\s+', last_paragraph)
        last_sentence = last_sentences[-1] if last_sentences else ""
        
        # If the last sentence already contains a question mark, assume it's a follow-up question
        if '?' in last_sentence:
            return response
            
        # If no question is present, add an appropriate follow-up from our list
        import random
        follow_up = random.choice(self.sales_follow_up_questions)
        
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
        
        # Check for direct sales keywords first - most efficient detection
        if self.detect_sales_keywords(query):
            self.logger.info("Sales triggers detected in query, routing to sales agent")
            return AgentType.SALES.value
        
        # Check conversation history for potential sales opportunity
        history = self.context_manager.get_conversation_history(limit=5)
        
        # After the second exchange, increase chance of routing to sales
        if len(history) >= 4:  # 4 items = 2 user messages + 2 agent responses
            self.logger.info("Multiple conversation exchanges detected, considering sales routing")
            
            # After several exchanges, have a higher likelihood of switching to sales agent
            # The more exchanges, the more likely to route to sales
            if len(history) >= 6:  # 6 items = 3 turns
                # Direct to sales agent with increasing probability based on conversation length
                if len(history) >= 8:  # 8 items = 4 turns
                    self.logger.info("Extended conversation detected, routing to sales agent")
                    return AgentType.SALES.value
                
                # Check if previous agent responses contain strong indicators for sales opportunity
                agent_responses = [item["content"] for item in history if not item.get("is_user", False)]
                joined_responses = " ".join(agent_responses)
                
                # Keywords in previous responses that indicate readiness for sales
                readiness_indicators = [
                    "coverage", "protect", "family", "recommend", "options", 
                    "policy", "premium", "deductible", "risk", "benefit",
                    "cost", "saving", "plan", "financial", "future"
                ]
                
                indicator_count = sum(1 for indicator in readiness_indicators if indicator in joined_responses.lower())
                
                # If multiple indicators are found in previous responses
                if indicator_count >= 3:
                    self.logger.info(f"Found {indicator_count} sales readiness indicators in previous responses")
                    return AgentType.SALES.value
            
            # For all multi-exchange conversations, check intent with LLM
            sales_intent_prompt = """
            You are analyzing a conversation to determine if it's appropriate to transition to sales.
            
            Previous conversation:
            {history}
            
            Current query: {query}
            
            Based only on the conversation above, is the user now discussing a situation or showing interest 
            that indicates they might benefit from insurance product recommendations? Be more inclined to 
            answer "yes" if there's any indication of personal circumstances or interest in specific insurance options.
            
            Answer with only 'yes' or 'no'.
            """
            
            # Format the history for the prompt
            formatted_history = self.context_manager.format_history(limit=5)
            
            # Create and run the chain
            from langchain_core.prompts import ChatPromptTemplate
            intent_prompt = ChatPromptTemplate.from_template(sales_intent_prompt)
            intent_model = self.model_provider.get_model("writer")
            intent_chain = intent_prompt | intent_model | self.output_protocol._default_parser
            
            # Check for sales intent
            intent_result = intent_chain.invoke({
                "history": formatted_history,
                "query": query
            }).strip().lower()
            
            self.logger.info(f"Sales intent detection result: {intent_result}")
            
            # If sales intent detected, route to sales agent
            if intent_result == "yes":
                self.logger.info("Routing to sales agent based on conversation context")
                return AgentType.SALES.value
        
        # If no sales intent detected, use standard routing
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
        # Check if the query is asking about conversation history
        if self.is_history_query(query):
            self.logger.info("Detected history query, providing conversation history")
            history = self.format_user_queries(limit=10)
            response = f"Here are your previous questions:\n\n{history}"
            
            # Don't append a follow-up question for meta-queries
            return {
                "agent": "system",
                "response": response
            }
        
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
        
        # Post-process response to ensure it has a follow-up question
        enhanced_response = self.ensure_follow_up_question(response, agent_type)
        
        # Store in context
        self.context_manager.add_interaction(query, agent_type, enhanced_response)
        
        # Return results
        return {
            "agent": agent_type,
            "response": enhanced_response
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
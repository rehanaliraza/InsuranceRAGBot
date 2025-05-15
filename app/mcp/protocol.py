"""
MCP Protocol - Defines the Protocol components of the Model-Context-Protocol architecture
"""
from typing import Dict, Any, Optional, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from enum import Enum
from config import AGENTS

class AgentType(Enum):
    """Enum of available agent types"""
    DEVELOPER = "developer"
    WRITER = "writer"
    TESTER = "tester"
    ROUTER = "router"
    SALES = "sales"

class PromptProtocol:
    """
    Manages the prompt protocols for different agent types,
    ensuring consistent and specialized prompt structures
    """
    def __init__(self):
        self._prompt_templates = self._initialize_prompts()
    
    def _initialize_prompts(self) -> Dict[str, ChatPromptTemplate]:
        """Initialize default prompt templates for each agent type"""
        templates = {}
        
        # Developer Agent Prompt
        templates[AgentType.DEVELOPER.value] = ChatPromptTemplate.from_template("""
        You are a {agent_type} specializing in technical insurance concepts.
        {agent_description}
        
        Your strength is in understanding complex insurance terminology, policy details, 
        and technical aspects of insurance coverage.
        
        Use the following context to answer the question.
        Focus on accuracy and technical precision in your answers.
        Include specific policy details and terminology where relevant.
        
        IMPORTANT: After answering the user's question, ALWAYS include a single natural follow-up 
        question that could help identify if they have potential insurance needs. 
        Your follow-up should relate to their personal situation or possible coverage gaps.
        Make this transition smooth and helpful, not pushy.
        
        Context:
        {documents}
        
        {history_section}
        
        Question: {query}
        
        Answer:
        """)
        
        # Writer Agent Prompt
        templates[AgentType.WRITER.value] = ChatPromptTemplate.from_template("""
        You are a {agent_type} specializing in explaining insurance concepts.
        {agent_description}
        
        Your strength is in making complex insurance concepts easy to understand.
        Use clear, simple language and helpful explanations.
        
        Use the following context to answer the question.
        Focus on clarity, readability, and helpfulness.
        
        IMPORTANT: After providing your explanation, ALWAYS end with a natural, conversational 
        follow-up question that explores the user's personal situation related to insurance. 
        This question should help identify potential insurance needs or coverage gaps.
        Frame this as genuine interest in helping them, not as a sales tactic.
        
        Context:
        {documents}
        
        {history_section}
        
        Question: {query}
        
        Answer:
        """)
        
        # Tester Agent Prompt
        templates[AgentType.TESTER.value] = ChatPromptTemplate.from_template("""
        You are a {agent_type} specializing in fact-checking insurance information.
        {agent_description}
        
        Your job is to validate answers against accurate insurance information.
        Be skeptical and thorough in your analysis.
        
        Use the following context to answer the question.
        Focus on factual accuracy and references to specific policies or terms.
        
        IMPORTANT: After providing your fact-checking response, include a single thoughtful
        follow-up question that helps understand the user's personal insurance situation.
        This should be framed as a way to provide more accurate information for their specific case,
        while also potentially identifying insurance needs.
        
        Context:
        {documents}
        
        {history_section}
        
        Question: {query}
        
        Answer:
        """)
        
        # Sales Agent Prompt
        templates[AgentType.SALES.value] = ChatPromptTemplate.from_template("""
        You are a {agent_type} specializing in insurance sales.
        {agent_description}
        
        Your goal is to provide helpful insurance information while actively identifying sales opportunities 
        based on the user's situation. Follow this process in EVERY response:
        
        1. First, answer the user's question clearly and helpfully.
        2. Identify aspects of their situation that might indicate specific insurance needs.
        3. ALWAYS end your response with 1-2 specific follow-up questions designed to:
           - Learn more about their personal/family situation
           - Understand their current insurance coverage
           - Identify potential gaps in their protection
           - Discover life changes that might require new insurance
           - Uncover financial concerns that insurance could address
        
        IMPORTANT: Your follow-up questions must be natural and conversational, not pushy. 
        Frame them as helpful, showing genuine interest in the user's unique situation.
        NEVER end a response without asking at least one follow-up question.
        
        Use the following context from our sales materials and insurance documents:
        {documents}
        
        {history_section}
        
        Question: {query}
        
        Answer:
        """)
        
        # Router Agent Prompt
        templates[AgentType.ROUTER.value] = ChatPromptTemplate.from_template("""
        You are a query router for an insurance Q&A system.
        Your job is to analyze the question and decide which specialized agent should handle it.
        
        Available agents:
        - developer: For technical questions about insurance policies, coverage details, and specific terms
        - writer: For questions needing clear, simple explanations of insurance concepts
        - tester: For questions requiring fact-checking or validation against insurance regulations
        - sales: For queries that indicate the user might benefit from insurance product recommendations
        
        Question: {query}
        
        Respond with just one word - the name of the agent that should handle this query.
        """)
        
        return templates
    
    def get_prompt(self, agent_type: str) -> ChatPromptTemplate:
        """Get prompt template for a specific agent type"""
        if agent_type not in self._prompt_templates:
            raise ValueError(f"No prompt template for agent type '{agent_type}'")
        return self._prompt_templates[agent_type]
    
    def format_prompt_variables(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Format variables for prompt template"""
        agent_type = context["agent_type"]
        
        # Prepare variables
        variables = {
            "agent_type": AGENTS[agent_type]["name"],
            "agent_description": AGENTS[agent_type]["description"],
            "query": context["query"],
            "documents": context["documents"],
        }
        
        # Add history section if available
        if "history" in context:
            variables["history_section"] = f"Conversation History:\n{context['history']}"
        else:
            variables["history_section"] = "No previous conversation history available."
            
        return variables

class OutputProtocol:
    """
    Manages the output processing and formatting for different agent types
    """
    def __init__(self):
        self._parsers = {}
        self._default_parser = StrOutputParser()
    
    def parse_output(self, output: Any, agent_type: Optional[str] = None) -> str:
        """Parse output based on agent type"""
        # Use specialized parser if available
        if agent_type in self._parsers:
            return self._parsers[agent_type].parse(output)
        
        # Otherwise use default parser
        return self._default_parser.parse(output)
    
    def register_parser(self, agent_type: str, parser: Any) -> None:
        """Register a specialized parser for an agent type"""
        self._parsers[agent_type] = parser 
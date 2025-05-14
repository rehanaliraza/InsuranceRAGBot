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
        
        Context:
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
            variables["history_section"] = f"Previous conversation:\n{context['history']}"
        else:
            variables["history_section"] = ""
            
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
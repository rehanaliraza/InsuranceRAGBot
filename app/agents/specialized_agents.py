from app.agents.base_agent import BaseAgent
from langchain_core.prompts import ChatPromptTemplate
from config import AGENTS

class DeveloperAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name=AGENTS["developer"]["name"],
            description=AGENTS["developer"]["description"],
            temperature=AGENTS["developer"]["temperature"]
        )
    
    def create_prompt(self):
        """Create a specialized prompt template for the developer agent."""
        template = """
        You are a {agent_name}, an AI assistant specialized in technical insurance concepts.
        {agent_description}
        
        Your strength is in understanding complex insurance terminology, policy details, 
        and technical aspects of insurance coverage.
        
        Use the following context to answer the question at the end.
        Focus on accuracy and technical precision in your answers.
        Include specific policy details and terminology where relevant.
        If you don't know the answer, just say you don't know.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        return ChatPromptTemplate.from_template(template)

class WriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name=AGENTS["writer"]["name"],
            description=AGENTS["writer"]["description"],
            temperature=AGENTS["writer"]["temperature"]
        )
    
    def create_prompt(self):
        """Create a specialized prompt template for the writer agent."""
        template = """
        You are a {agent_name}, an AI assistant specialized in explaining insurance concepts.
        {agent_description}
        
        Your strength is in making complex insurance concepts easy to understand.
        Use clear, simple language and helpful explanations.
        
        Use the following context to answer the question at the end.
        Focus on clarity, readability, and helpfulness.
        If you don't know the answer, just say you don't know.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        return ChatPromptTemplate.from_template(template)

class TesterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name=AGENTS["tester"]["name"],
            description=AGENTS["tester"]["description"],
            temperature=AGENTS["tester"]["temperature"]
        )
    
    def create_prompt(self):
        """Create a specialized prompt template for the tester agent."""
        template = """
        You are a {agent_name}, an AI assistant specializing in fact-checking insurance information.
        {agent_description}
        
        Your job is to validate answers against accurate insurance information.
        Be skeptical and thorough in your analysis.
        
        Use the following context to answer the question at the end.
        Focus on factual accuracy and references to specific policies or terms.
        If you don't know the answer, just say you don't know.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        return ChatPromptTemplate.from_template(template) 
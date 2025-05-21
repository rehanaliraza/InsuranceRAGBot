from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.agents.specialized_agents import DeveloperAgent, WriterAgent, TesterAgent
from config import OPENAI_API_KEY

class MasterControlProgram:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            openai_api_key=OPENAI_API_KEY
        )
        self.agents = {
            "developer": DeveloperAgent(),
            "writer": WriterAgent(),
            "tester": TesterAgent()
        }
        self.memory = []
        
    def route_query(self, query):
        """Determine which agent should handle the query."""
        router_prompt = ChatPromptTemplate.from_template("""
        You are a query router for a general-purpose Q&A system.
        Your job is to analyze the question and decide which specialized agent should handle it.
        
        Available agents:
        - developer: For technical questions requiring detailed explanations and specialized knowledge
        - writer: For questions needing clear, simple explanations of complex concepts
        - tester: For questions requiring fact-checking or validation of information
        
        Question: {question}
        
        Respond with just one word - the name of the agent that should handle this query.
        """)
        
        chain = router_prompt | self.llm | StrOutputParser()
        agent_name = chain.invoke({"question": query}).strip().lower()
        
        # Default to writer if no valid agent is returned
        if agent_name not in self.agents:
            agent_name = "writer"
            
        return agent_name
        
    def process_query(self, query, agent_name=None):
        """Process a query using the appropriate agent."""
        if agent_name is None:
            agent_name = self.route_query(query)
            
        agent = self.agents[agent_name]
        response = agent.process(query)
        
        # Store in memory
        self.memory.append({
            "query": query,
            "agent": agent_name,
            "response": response
        })
        
        return {
            "agent": agent_name,
            "response": response
        }
        
    def process_with_review(self, query):
        """Process a query with the primary agent and then review with the tester agent."""
        # First, route and process with primary agent
        primary_agent = self.route_query(query)
        primary_result = self.agents[primary_agent].process(query)
        
        # Then, have the tester agent validate the answer
        validation_query = f"Question: {query}\n\nProposed answer: {primary_result}\n\nIs this answer accurate based on the available information?"
        validation_result = self.agents["tester"].process(validation_query)
        
        # Store in memory
        self.memory.append({
            "query": query,
            "primary_agent": primary_agent,
            "primary_response": primary_result,
            "validation": validation_result
        })
        
        return {
            "primary_agent": primary_agent,
            "response": primary_result,
            "validation": validation_result
        } 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.utils.vectorstore import get_relevant_documents
from config import OPENAI_API_KEY

class BaseAgent:
    def __init__(self, name, description, temperature=0.7):
        self.name = name
        self.description = description
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=temperature,
            openai_api_key=OPENAI_API_KEY
        )
        
    def format_docs(self, docs):
        """Format documents into a string."""
        return "\n\n".join(doc.page_content for doc in docs)
        
    def create_prompt(self):
        """Create the default prompt template for the agent."""
        template = """
        You are a {agent_name}, an AI assistant specialized in insurance.
        {agent_description}
        
        Use the following context to answer the question at the end.
        If you don't know the answer, just say you don't know.
        Do not make up information that is not in the context.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        return ChatPromptTemplate.from_template(template)
    
    def create_chain(self):
        """Create the default chain for the agent."""
        prompt = self.create_prompt()
        
        chain = (
            {"context": lambda x: self.format_docs(get_relevant_documents(x["question"])), 
             "question": lambda x: x["question"],
             "agent_name": lambda _: self.name,
             "agent_description": lambda _: self.description}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return chain
    
    def process(self, query):
        """Process a query using the agent's chain."""
        chain = self.create_chain()
        return chain.invoke({"question": query}) 
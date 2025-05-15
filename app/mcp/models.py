"""
MCP Models - Defines the Model components of the Model-Context-Protocol architecture
"""
from langchain_core.language_models.base import BaseLanguageModel
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY

class ModelProvider:
    """
    Provides access to different language models with consistent configuration
    """
    def __init__(self):
        self._models = {}
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize default model configurations"""
        # Technical model - precise, low temperature
        self._models["developer"] = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Writer model - balanced
        self._models["writer"] = ChatOpenAI(
            model="gpt-4",
            temperature=0.5,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Verification model - factual, no temperature
        self._models["tester"] = ChatOpenAI(
            model="gpt-4",
            temperature=0.0,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Sales model - creative, higher temperature
        self._models["sales"] = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Router model - for query classification
        self._models["router"] = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.0, 
            openai_api_key=OPENAI_API_KEY
        )
    
    def get_model(self, model_type: str) -> BaseLanguageModel:
        """Get a language model by type"""
        if model_type not in self._models:
            raise ValueError(f"Model type '{model_type}' not available")
        return self._models[model_type]
    
    def register_model(self, model_type: str, model: BaseLanguageModel):
        """Register a new model"""
        self._models[model_type] = model 
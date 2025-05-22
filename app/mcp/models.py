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
        self._model_names = {}  # Track model names for metrics
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize default model configurations"""
        # Technical model - precise, low temperature
        self._models["developer"] = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            openai_api_key=OPENAI_API_KEY
        )
        self._model_names["developer"] = "gpt-4"
        
        # Writer model - balanced
        self._models["writer"] = ChatOpenAI(
            model="gpt-4",
            temperature=0.5,
            openai_api_key=OPENAI_API_KEY
        )
        self._model_names["writer"] = "gpt-4"
        
        # Verification model - factual, no temperature
        self._models["tester"] = ChatOpenAI(
            model="gpt-4",
            temperature=0.0,
            openai_api_key=OPENAI_API_KEY
        )
        self._model_names["tester"] = "gpt-4"
        
        # Router model - for query classification
        self._models["router"] = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.0, 
            openai_api_key=OPENAI_API_KEY
        )
        self._model_names["router"] = "gpt-3.5-turbo"
    
    def get_model(self, model_type: str) -> BaseLanguageModel:
        """Get a language model by type"""
        if model_type not in self._models:
            raise ValueError(f"Model type '{model_type}' not available")
        return self._models[model_type]
    
    def get_model_name(self, model_type: str) -> str:
        """Get the name of the model used for a specific agent type"""
        if model_type not in self._model_names:
            return "unknown"
        return self._model_names[model_type]
    
    def register_model(self, model_type: str, model: BaseLanguageModel, model_name: str = None):
        """Register a new model"""
        self._models[model_type] = model
        
        # Store the model name if provided
        if model_name:
            self._model_names[model_type] = model_name
        # Try to extract model name from the model object if possible
        elif hasattr(model, 'model'):
            self._model_names[model_type] = model.model
        else:
            self._model_names[model_type] = str(type(model).__name__) 
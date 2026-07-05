import os
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class LLMClientBase(ABC):
    @abstractmethod
    def chat(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        pass


class MockLLMClient(LLMClientBase):
    def __init__(self):
        self.responses = {
            "strategy": "Based on the market analysis, I recommend a BUY signal for tech stocks.",
            "analysis": "The current market shows strong momentum with positive sentiment indicators.",
            "optimization": "I've optimized the strategy by adjusting the RSI threshold from 70 to 65.",
            "default": "This is a mock response from the LLM client."
        }
    
    def chat(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2000) -> str:
        logger.info(f"Generating mock response for prompt containing: {prompt[:50]}...")
        for key, response in self.responses.items():
            if key.lower() in prompt.lower():
                return response
        return self.responses["default"]


class LLMClient:
    def __init__(self, config: Dict[str, Any] = None):
        self.models = {
            'gpt-4o': MockLLMClient(),
            'deepseek': MockLLMClient(),
            'kimi': MockLLMClient(),
            'glm': MockLLMClient()
        }
        self.current_model = config.get('default', 'gpt-4o') if config else 'gpt-4o'
    
    def chat(self, prompt: str, model_name: Optional[str] = None, 
             temperature: float = 0.3, max_tokens: int = 2000) -> str:
        model_to_use = model_name or self.current_model
        client = self.models.get(model_to_use)
        
        if not client:
            raise ValueError(f"Model not found: {model_to_use}")
        
        return client.chat(prompt, temperature, max_tokens)
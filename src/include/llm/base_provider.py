from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    tokens_used: int
    cost: float
    latency_ms: float
    confidence: float = 1.0


class BaseLLMProvider(ABC):
    def __init__(self, api_key: str, model: str, temperature: float = 0.1, max_tokens: int = 1500):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
    
    @abstractmethod
    def extract_invoice_data(
        self, 
        pdf_text: str, 
        system_prompt: str,
        invoice_schema: Dict[str, Any]
    ) -> LLMResponse:
        pass
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        pricing = self._get_pricing()
        return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
    
    @abstractmethod
    def _get_pricing(self) -> Dict[str, float]:
        pass

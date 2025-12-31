import json
import time
from typing import Dict, Any
from anthropic import Anthropic
from .base_provider import BaseLLMProvider, LLMResponse


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = Anthropic(api_key=api_key)
    
    def extract_invoice_data(
        self, 
        pdf_text: str, 
        system_prompt: str,
        invoice_schema: Dict[str, Any]
    ) -> LLMResponse:
        start_time = time.time()
        
        user_prompt = f"""{system_prompt}\n\nExtract from this UberEats invoice:\n\n{pdf_text[:3500]}\n\nReturn JSON matching: {json.dumps(invoice_schema)}"""
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{
                "role": "user",
                "content": user_prompt
            }]
        )
        
        latency_ms = (time.time() - start_time) * 1000
        usage = response.usage
        cost = self._calculate_cost(usage.input_tokens, usage.output_tokens)
        
        return LLMResponse(
            content=response.content[0].text,
            provider="anthropic",
            model=self.model,
            tokens_used=usage.input_tokens + usage.output_tokens,
            cost=cost,
            latency_ms=latency_ms
        )
    
    def _get_pricing(self) -> Dict[str, float]:
        pricing_map = {
            "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
            "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
            "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25}
        }
        return pricing_map.get(self.model, {"input": 0.25, "output": 1.25})

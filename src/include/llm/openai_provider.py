import json
import time
from typing import Dict, Any
from openai import OpenAI
from .base_provider import BaseLLMProvider, LLMResponse


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = OpenAI(api_key=api_key)
    
    def extract_invoice_data(
        self, 
        pdf_text: str, 
        system_prompt: str,
        invoice_schema: Dict[str, Any]
    ) -> LLMResponse:
        start_time = time.time()
        
        user_prompt = f"""Extract from this UberEats invoice:\n\n{pdf_text[:3500]}\n\nReturn JSON matching: {json.dumps(invoice_schema)}"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"}
        )
        
        latency_ms = (time.time() - start_time) * 1000
        usage = response.usage
        cost = self._calculate_cost(usage.prompt_tokens, usage.completion_tokens)
        
        return LLMResponse(
            content=response.choices[0].message.content,
            provider="openai",
            model=self.model,
            tokens_used=usage.total_tokens,
            cost=cost,
            latency_ms=latency_ms
        )
    
    def _get_pricing(self) -> Dict[str, float]:
        pricing_map = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00}
        }
        return pricing_map.get(self.model, {"input": 0.15, "output": 0.60})

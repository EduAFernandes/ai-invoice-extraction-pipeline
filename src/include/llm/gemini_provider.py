import json
import time
from typing import Dict, Any
import google.generativeai as genai
from .base_provider import BaseLLMProvider, LLMResponse


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", **kwargs):
        super().__init__(api_key, model, **kwargs)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)
    
    def extract_invoice_data(
        self, 
        pdf_text: str, 
        system_prompt: str,
        invoice_schema: Dict[str, Any]
    ) -> LLMResponse:
        start_time = time.time()
        
        user_prompt = f"""{system_prompt}\n\nExtract from this UberEats invoice:\n\n{pdf_text[:3500]}\n\nReturn JSON matching: {json.dumps(invoice_schema)}"""
        
        response = self.client.generate_content(
            user_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                response_mime_type="application/json"
            )
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
        cost = self._calculate_cost(input_tokens, output_tokens)
        
        return LLMResponse(
            content=response.text,
            provider="gemini",
            model=self.model,
            tokens_used=input_tokens + output_tokens,
            cost=cost,
            latency_ms=latency_ms
        )
    
    def _get_pricing(self) -> Dict[str, float]:
        pricing_map = {
            "gemini-1.5-flash": {"input": 0.0, "output": 0.0},
            "gemini-1.5-pro": {"input": 1.25, "output": 5.00}
        }
        return pricing_map.get(self.model, {"input": 0.0, "output": 0.0})

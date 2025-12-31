from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class InvoiceItem(BaseModel):
    nome: str = Field(..., min_length=1)
    quantidade: int = Field(..., ge=1)
    preco_unitario: float = Field(..., ge=0)
    preco_total: float = Field(..., ge=0)
    
    @field_validator('preco_total')
    @classmethod
    def validate_total(cls, v, info):
        if 'quantidade' in info.data and 'preco_unitario' in info.data:
            expected = info.data['quantidade'] * info.data['preco_unitario']
            if abs(v - expected) > 0.01:
                raise ValueError(f"Item total mismatch: {v} != {expected:.2f}")
        return v


class InvoiceData(BaseModel):
    order_id: str = Field(..., min_length=1)
    restaurante: str = Field(..., min_length=1)
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    data_hora: datetime
    itens: List[InvoiceItem] = Field(..., min_length=1)
    subtotal: float = Field(..., ge=0)
    taxa_entrega: float = Field(default=0.0, ge=0)
    taxa_servico: float = Field(default=0.0, ge=0)
    gorjeta: float = Field(default=0.0, ge=0)
    total: float = Field(..., ge=0)
    pagamento: Optional[str] = None
    endereco_entrega: Optional[str] = None
    tempo_entrega: Optional[str] = None
    entregador: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_invoice_total(self):
        expected_total = (
            self.subtotal + 
            self.taxa_entrega + 
            self.taxa_servico + 
            self.gorjeta
        )
        
        if abs(self.total - expected_total) > 0.01:
            raise ValueError(
                f"Invoice total mismatch: {self.total} != {expected_total:.2f} "
                f"(subtotal={self.subtotal}, delivery={self.taxa_entrega}, "
                f"service={self.taxa_servico}, tip={self.gorjeta})"
            )
        
        items_subtotal = sum(item.preco_total for item in self.itens)
        if abs(self.subtotal - items_subtotal) > 0.01:
            raise ValueError(
                f"Subtotal mismatch: {self.subtotal} != items_sum={items_subtotal:.2f}"
            )
        
        return self
    
    @field_validator('data_hora', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except Exception:
                raise ValueError(f"Invalid datetime format: {v}")
        return v


class ExtractionResult(BaseModel):
    invoice_data: InvoiceData
    file_key: str
    provider: str
    model: str
    tokens_used: int
    cost: float
    latency_ms: float
    confidence: float = 1.0
    validation_passed: bool = True
    validation_errors: List[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True

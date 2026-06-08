from pydantic import BaseModel, Field
from datetime import datetime

class EventBase(BaseModel):
    name: str = Field(..., min_length=1, description="Nome do evento")
    date: datetime = Field(..., description="Data do evento")
    price: float = Field(..., gt=0, description="Preço do ingresso")
    available_quantity: int = Field(..., ge=0, description="Quantidade de ingressos disponíveis")

class EventCreate(EventBase):
    pass

class EventUpdateQuantity(BaseModel):
    available_quantity: int = Field(..., ge=0, description="Nova quantidade de ingressos disponíveis")

class EventUpdatePrice(BaseModel):
    price: float = Field(..., gt=0, description="Novo preço do ingresso")

class EventResponse(EventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class EventReserveRequest(BaseModel):
    quantity: int = Field(..., gt=0, description="Quantidade de ingressos para reservar")

class EventReserveResponse(BaseModel):
    message: str
    event_id: int
    reserved_quantity: int
    total_amount: float

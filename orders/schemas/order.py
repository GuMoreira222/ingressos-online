from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from models.order import OrderStatus, PaymentMethod


class OrderCreate(BaseModel):
    event_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    payment_method: PaymentMethod


class OrderResponse(BaseModel):
    id: int
    user_id: str
    event_id: int
    quantity: int
    payment_method: PaymentMethod
    status: OrderStatus
    payment_id: int | None = None
    failure_reason: str | None = None
    idempotency_key: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

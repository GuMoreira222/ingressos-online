from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    order_id: int = Field(..., gt=0)
    user_id: str = Field(..., min_length=1)
    amount: float = Field(..., gt=0)
    method: PaymentMethod
    force_reject: bool = False


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    user_id: str
    amount: float
    method: PaymentMethod
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

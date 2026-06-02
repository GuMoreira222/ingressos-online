import enum
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, Integer, String
from db.database import Base


class PaymentMethod(str, enum.Enum):
    PIX = "pix"
    BOLETO = "boleto"
    CREDIT_CARD = "credit_card"


class OrderStatus(str, enum.Enum):
    CREATED = "created"
    RESERVED = "reserved"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    event_id = Column(Integer, index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.CREATED, nullable=False)
    payment_id = Column(Integer, nullable=True)
    failure_reason = Column(String, nullable=True)
    idempotency_key = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

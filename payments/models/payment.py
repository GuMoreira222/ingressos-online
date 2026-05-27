import enum
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, Float, Integer, String
from db.database import Base


class PaymentMethod(str, enum.Enum):
    PIX = "pix"
    BOLETO = "boleto"
    CREDIT_CARD = "credit_card"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

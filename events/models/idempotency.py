from sqlalchemy import Column, String, DateTime
from db.database import Base
from datetime import datetime, timezone

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    key = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

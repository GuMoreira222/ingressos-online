from sqlalchemy import Column, Integer, String, Float, DateTime
from db.database import Base
from datetime import datetime, timezone

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    available_quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

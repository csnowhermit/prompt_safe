from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.core.database import Base


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(36), nullable=False)
    event_type = Column(String(50), nullable=False)
    risk_level = Column(String(10), nullable=False)
    layer = Column(String(10), nullable=False)
    rule_id = Column(String(50))
    user_hash = Column(String(64))
    session_id = Column(String(36))
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
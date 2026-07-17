from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime
from datetime import datetime

from app.core.database import Base


class ToolRegistry(Base):
    __tablename__ = "tool_registry"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    auth_level = Column(String(20), nullable=False)
    params_schema = Column(JSON, nullable=False)
    rate_limit = Column(JSON)
    requires_approval = Column(Boolean, default=False)
    requires_mfa = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
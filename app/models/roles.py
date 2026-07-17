from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime

from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), unique=True, nullable=False)
    description = Column(String(200))
    permissions = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
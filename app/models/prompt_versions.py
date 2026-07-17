from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, UniqueConstraint
from datetime import datetime

from app.core.database import Base


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String(20), nullable=False)
    scenario = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False)
    change_log = Column(JSON)
    review_status = Column(String(20), default="draft")
    reviewer = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("role", "scenario", "version", name="uq_role_scenario_version"),
    )
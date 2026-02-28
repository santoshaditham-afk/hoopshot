from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from .audit_db import AuditBase


class PRApproval(AuditBase):
    __tablename__ = "pr_approvals"

    id = Column(Integer, primary_key=True, index=True)
    pr_number = Column(Integer, nullable=True)
    pr_title = Column(String, nullable=True)
    pr_author = Column(String, nullable=True)
    artifact_hash = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    approved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scores = relationship("Score", back_populates="user")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Integer, nullable=False)
    shots_taken = Column(Integer, nullable=False)
    shots_made = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="scores")


class MergeCheckpoint(Base):
    __tablename__ = "merge_checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    commit_sha = Column(String, unique=True, index=True, nullable=False)
    content_hash = Column(String, nullable=False)
    branch = Column(String, nullable=False)
    author = Column(String, nullable=False)
    message = Column(String, nullable=False)
    merged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

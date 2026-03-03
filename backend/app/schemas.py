from __future__ import annotations
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ScoreCreate(BaseModel):
    score: int
    shots_taken: int
    shots_made: int


class ScoreOut(BaseModel):
    id: int
    score: int
    shots_taken: int
    shots_made: int
    created_at: datetime
    username: Optional[str] = None

    model_config = {"from_attributes": True}

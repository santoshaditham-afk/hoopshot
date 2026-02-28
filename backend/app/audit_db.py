from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os

os.makedirs("data", exist_ok=True)

AUDIT_DATABASE_URL = "sqlite:///./data/pr_audit.db"

audit_engine = create_engine(AUDIT_DATABASE_URL, connect_args={"check_same_thread": False})
AuditSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=audit_engine)


class AuditBase(DeclarativeBase):
    pass


def get_audit_db():
    db = AuditSessionLocal()
    try:
        yield db
    finally:
        db.close()

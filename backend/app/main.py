from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .audit_db import audit_engine, AuditBase
from .audit_models import PRApproval  # noqa: F401 — registers model with AuditBase
from .routers import auth, scores

Base.metadata.create_all(bind=engine)
AuditBase.metadata.create_all(bind=audit_engine)

app = FastAPI(title="HoopShot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(scores.router)


@app.get("/health")
def health():
    return {"status": "ok"}

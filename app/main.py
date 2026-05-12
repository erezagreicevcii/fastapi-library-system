from fastapi import FastAPI

from app.database import Base, engine
from app import models

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Library Lending API",
    version="1.0.0",
)

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "library": "open"}

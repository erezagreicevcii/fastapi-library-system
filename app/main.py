from fastapi import FastAPI

from app import models
from app.database import Base, engine
from app.routers import authors, categories

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Lending API",
    version="1.0.0",
)

app.include_router(categories.router, prefix="/api/v1")
app.include_router(authors.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "library": "open"}

from fastapi import FastAPI

from app.routers import authors, categories, members, books, loans, reports


app = FastAPI(
    title="Library Lending API",
    version="1.0.0",
)

app.include_router(categories.router, prefix="/api/v1")
app.include_router(authors.router, prefix="/api/v1")
app.include_router(members.router, prefix="/api/v1")
app.include_router(books.router, prefix="/api/v1")
app.include_router(loans.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "library": "open"}

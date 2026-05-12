from fastapi import FastAPI

app = FastAPI(
    title="Library Lending API",
    version="1.0.0",
)

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "library": "open"}


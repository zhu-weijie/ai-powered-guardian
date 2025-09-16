from fastapi import FastAPI
from app.api.api import api_router

app = FastAPI(title="AI-Powered Guardian API")

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the AI-Powered Guardian API"}

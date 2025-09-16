from fastapi import FastAPI

app = FastAPI(title="AI-Powered Guardian API")


@app.get("/")
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the AI-Powered Guardian API"}

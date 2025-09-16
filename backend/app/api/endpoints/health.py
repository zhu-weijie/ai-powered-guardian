from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import SessionLocal
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


def get_db():
    """Dependency to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def check_health(db: Session = Depends(get_db)):
    """
    Checks the health of the API and its database connection.
    """
    try:
        # Use db.execute(text(...)) to perform a simple query
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_status = "error"

    return {"api_status": "ok", "db_status": db_status}

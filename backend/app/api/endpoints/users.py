from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import user as crud_user
from app.schemas.user import User

router = APIRouter()


@router.get("/", response_model=list[User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user),
):
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users

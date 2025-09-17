from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import role as crud_role
from app.schemas.role import Role, RoleCreate
from app.models.user import User  # Import the User model for type hinting

router = APIRouter()


@router.post("/", response_model=Role)
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user),  # Correctly typed
):
    # The current_user is validated by the dependency but not used in the function body.
    # This is a common pattern for authorization.
    return crud_role.create_role(db=db, role=role_in)


@router.get("/", response_model=list[Role])
def read_roles(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user),  # Correctly typed
):
    return crud_role.get_roles(db=db)

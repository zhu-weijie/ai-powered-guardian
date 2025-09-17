from sqlalchemy.orm import Session
from app.models.role import Role
from app.schemas.role import RoleCreate


def create_role(db: Session, role: RoleCreate) -> Role:
    db_role = Role(name=role.name, description=role.description)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


def get_roles(db: Session, skip: int = 0, limit: int = 100) -> list[Role]:
    return db.query(Role).offset(skip).limit(limit).all()

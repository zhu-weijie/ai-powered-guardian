from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship  # Import relationship
from app.db.base_class import Base


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    # Add a back-populating relationship to the User model
    users = relationship("User", secondary="user_roles", back_populates="roles")

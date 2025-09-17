from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

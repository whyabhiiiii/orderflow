from pydantic import BaseModel, EmailStr

from app.models.user import Role


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: Role
    phone: str | None = None
    address: str | None = None
    cuisine_type: str | None = None


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    role: Role
    phone: str | None
    is_active: bool
    address: str | None = None
    cuisine_type: str | None = None
    latitude: float | None = None
    longitude: float | None = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    picture: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
    is_active: bool
    is_fake_login: bool

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(..., min_length=1)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class FakeLoginRequest(BaseModel):
    email: Optional[str] = "dev@example.com"

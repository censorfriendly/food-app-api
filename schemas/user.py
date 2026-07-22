
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str = Field(..., min_length=1, max_length=255)
    name: str | None = Field(None, max_length=255)
    picture: str | None = None


class UserOut(BaseModel):
    id: int
    email: str
    name: str | None = None
    picture: str | None = None
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
    email: str | None = "dev@example.com"

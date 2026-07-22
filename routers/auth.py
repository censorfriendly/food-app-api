from fastapi import APIRouter, HTTPException

from config.settings import get_settings
from core.deps import CurrentUser, DbSession, RefreshToken
from exceptions.custom import ValidationError
from schemas.common import SuccessResponse
from schemas.user import FakeLoginRequest, GoogleLoginRequest
from services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/fake-login", response_model=SuccessResponse)
async def fake_login(request: FakeLoginRequest, db: DbSession):
    """
    Development-only endpoint that returns fake JWT tokens and a user profile.
    REMOVE BEFORE PRODUCTION.
    """
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    auth_service = AuthService(db)
    try:
        data = auth_service.fake_login(request.email)
        return SuccessResponse(data=data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Login failed") from exc


@router.post("/google", response_model=SuccessResponse)
async def google_login(request: GoogleLoginRequest, db: DbSession):
    """Validate Google ID token and return JWT tokens + user profile."""
    auth_service = AuthService(db)
    try:
        data = auth_service.google_login(request.id_token)
        return SuccessResponse(data=data)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e)) from e
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Google login failed") from exc


@router.post("/refresh", response_model=SuccessResponse)
async def refresh_token(refresh_token: RefreshToken, db: DbSession):
    """Refresh access token using a valid refresh token from the Authorization header."""
    auth_service = AuthService(db)
    try:
        data = auth_service.refresh(refresh_token)
        return SuccessResponse(data=data)
    except ValueError as e:
        raise ValidationError(str(e)) from e
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Token refresh failed") from exc


@router.post("/logout", response_model=SuccessResponse)
async def logout(current_user: CurrentUser):
    """End the client session; token revocation requires server-side token storage."""
    return SuccessResponse(data={"message": "Logged out successfully", "user_id": current_user["user"].id})

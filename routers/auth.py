from fastapi import APIRouter, Depends, HTTPException

from core.deps import DbSession
from exceptions.custom import ValidationError
from schemas.common import SuccessResponse
from schemas.user import FakeLoginRequest, GoogleLoginRequest, RefreshTokenRequest
from services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/fake-login", response_model=SuccessResponse)
async def fake_login(request: FakeLoginRequest, db: DbSession):
    """
    Development-only endpoint that returns fake JWT tokens and a user profile.
    REMOVE BEFORE PRODUCTION.
    """
    auth_service = AuthService(db)
    try:
        data = auth_service.fake_login(request.email)
        return SuccessResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/google", response_model=SuccessResponse)
async def google_login(request: GoogleLoginRequest, db: DbSession):
    """Validate Google ID token and return JWT tokens + user profile."""
    auth_service = AuthService(db)
    try:
        data = auth_service.google_login(request.id_token)
        return SuccessResponse(data=data)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Google login failed")


@router.post("/refresh", response_model=SuccessResponse)
async def refresh_token(request: RefreshTokenRequest, db: DbSession):
    """Refresh access token using a valid refresh token."""
    auth_service = AuthService(db)
    try:
        data = auth_service.refresh(request.refresh_token)
        return SuccessResponse(data=data)
    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Token refresh failed")


@router.post("/logout", response_model=SuccessResponse)
async def logout(db: DbSession):
    """Invalidate current session."""
    # TODO: Implement with authenticated user context
    return SuccessResponse(data={"message": "Logged out successfully"})

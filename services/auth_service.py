from datetime import datetime, timezone
import hashlib
import time

from sqlalchemy.orm import Session

from config.settings import get_settings
from core.security import create_access_token, create_refresh_token
from models.user import User
from repositories.user_repository import UserRepository
from schemas.user import UserOut

settings = get_settings()


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def _build_token_pair(self, user: User) -> dict:
        payload = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": UserOut.model_validate(user).model_dump(),
        }

    def fake_login(self, email: str = "dev@example.com") -> dict:
        """Development-only login that returns fake tokens."""
        user = self.user_repo.get_by_email(email)

        if not user:
            user = User(
                email=email,
                name="Developer User",
                is_fake_login=True,
                last_login_at=datetime.now(timezone.utc),
            )
            self.user_repo.create(user)

        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()

        return self._build_token_pair(user)

    def google_login(self, id_token: str) -> dict:
        """
        Validate Google ID token and return JWT tokens + user profile.
        TODO: Integrate google-auth library for token verification.
        """
        # TODO: Verify id_token with Google
        # info = google.oauth2.id_token.verify_oauth2_token(id_token, google.auth.transport.requests.Request())
        # google_sub = info["sub"]
        # email = info["email"]
        # name = info.get("name")
        # picture = info.get("picture")

        # For now, placeholder — real implementation requires Google OAuth credentials
        raise NotImplementedError("Google SSO requires valid OAuth credentials")

    def refresh(self, refresh_token: str) -> dict:
        """
        Validate refresh token and issue new token pair.
        TODO: Implement token blacklist / rotation.
        """
        from core.security import decode_token

        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")

        user = self.user_repo.get_by_id(int(user_id))
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        return self._build_token_pair(user)

    def logout(self, user_id: int) -> bool:
        """
        Invalidate session.
        TODO: Add token blacklist table for revoking tokens before expiry.
        """
        return True

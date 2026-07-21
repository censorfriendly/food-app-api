from datetime import datetime, timezone
import hashlib
import time

from sqlalchemy.orm import Session

from config.settings import get_settings
from core.security import create_access_token, create_refresh_token
from models.household import Household
from models.household_member import HouseholdMember
from models.user import User
from repositories.user_repository import UserRepository

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
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.first_name or user.email,
                "is_active": user.is_active,
                "is_fake_login": user.is_fake_login,
                "default_household_id": user.default_household_id,
            },
        }

    def _create_default_household(self, user: User) -> None:
        household = Household(name=f"{user.first_name or 'My'} Household", owner_user_id=user.id, timezone="UTC")
        self.db.add(household)
        self.db.flush()

        membership = HouseholdMember(household_id=household.id, user_id=user.id, role="Owner", is_active=True)
        self.db.add(membership)
        user.default_household_id = household.id

    def fake_login(self, email: str = "dev@example.com") -> dict:
        """Development-only login that returns fake tokens."""
        user = self.user_repo.get_by_email(email)

        if not user:
            user = User(
                email=email,
                first_name="Developer",
                last_name="User",
                is_fake_login=True,
                last_login_at=datetime.now(timezone.utc),
            )
            self.user_repo.create(user)
            self._create_default_household(user)
            self.db.commit()

        if not user.default_household_id:
            household = (
                self.db.query(Household)
                .join(HouseholdMember)
                .filter(HouseholdMember.user_id == user.id, HouseholdMember.is_active.is_(True))
                .first()
            )
            if household:
                user.default_household_id = household.id
            else:
                self._create_default_household(user)

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

        user = self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        return self._build_token_pair(user)

    def logout(self, user_id: int) -> bool:
        """
        Invalidate session.
        TODO: Add token blacklist table for revoking tokens before expiry.
        """
        return True

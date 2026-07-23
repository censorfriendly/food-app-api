from datetime import UTC, datetime

from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from config.settings import get_settings
from core.security import create_access_token, create_refresh_token, decode_token
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
                last_login_at=datetime.now(UTC),
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

        user.last_login_at = datetime.now(UTC)
        self.db.commit()

        return self._build_token_pair(user)

    def google_login(self, token: str) -> dict:
        """
        Verify Google ID token, find or create the user, and return JWT tokens.
        """
        info = id_token.verify_oauth2_token(token, requests.Request(), get_settings().GOOGLE_CLIENT_ID)

        if info["iss"] not in [
            "accounts.google.com",
            "https://accounts.google.com",
        ]:
            raise ValueError("Invalid Google issuer")

        google_id = info["sub"]
        email = info["email"]
        full_name = info.get("name", "")
        first_name, last_name = (full_name.split(" ", 1) + [None] * 2)[:2] if full_name else (None, None)

        # Look up existing user by provider
        user = self.user_repo.get_by_provider("google", google_id)

        if not user:
            # Check if an account with this email already exists
            user = self.user_repo.get_by_email(email)
            if user and not user.auth_provider:
                # Link Google to existing account
                user.auth_provider = "google"
                user.provider_user_id = google_id
            elif not user:
                # Create new user
                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    auth_provider="google",
                    provider_user_id=google_id,
                    last_login_at=datetime.now(UTC),
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

        user.last_login_at = datetime.now(UTC)
        self.db.commit()
        return self._build_token_pair(user)

    def refresh(self, refresh_token: str) -> dict:
        """
        Validate refresh token and issue new token pair.
        TODO: Implement token blacklist / rotation.
        """

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

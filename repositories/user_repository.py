from sqlalchemy.orm import Session

from models.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    @property
    def model_type(self):
        return User

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_provider(self, auth_provider: str, provider_user_id: str) -> User | None:
        """Find a user by their auth provider and provider-specific ID."""
        return (
            self.db.query(User)
            .filter(User.auth_provider == auth_provider, User.provider_user_id == provider_user_id)
            .first()
        )

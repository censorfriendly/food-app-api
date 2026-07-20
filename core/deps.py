from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from database.connection import get_db as get_db_session
from core.security import get_current_user_from_token
from exceptions.custom import AuthenticationError

security = HTTPBearer()


def get_db() -> Session:
    return next(get_db_session())


DbSession = Annotated[Session, Depends(get_db)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: DbSession,
):
    """Extract and validate the current user from the Authorization header."""
    token = credentials.credentials
    payload = get_current_user_from_token(token)

    # TODO: Query database to verify user exists and is active
    # user = db.query(User).filter(User.id == payload["sub"]).first()
    # if not user or not user.is_active:
    #     raise AuthenticationError("User not found or inactive")

    return payload


CurrentUser = Annotated[dict, Depends(get_current_user)]

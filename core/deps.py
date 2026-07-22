from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from core.security import get_current_user_from_token, validate_refresh_token
from database.connection import get_db as get_db_session
from exceptions.custom import AuthenticationError
from models.user import User

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
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")

    return {"user": user, "token_payload": payload}


CurrentUser = Annotated[dict, Depends(get_current_user)]


async def get_refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    """Extract and validate a refresh token from the Authorization header.

    Returns the raw token string so the caller can decide how to use it.
    Raises AuthenticationError if the token is missing, malformed, or not
    a refresh-type token.
    """
    token = credentials.credentials
    validate_refresh_token(token)
    return token


RefreshToken = Annotated[str, Depends(get_refresh_token)]


def get_household_id(current_user: dict) -> str:
    """Return the user's selected active household.

    Household membership, rather than ownership, is the authorization boundary.
    """
    user = current_user["user"]
    active_memberships = [membership for membership in user.household_members if membership.is_active]
    household_ids = {membership.household_id for membership in active_memberships}
    household_id = (
        user.default_household_id
        if user.default_household_id in household_ids
        else active_memberships[0].household_id
        if active_memberships
        else None
    )
    if not household_id:
        raise HTTPException(status_code=400, detail="User is not attached to a household")
    return household_id

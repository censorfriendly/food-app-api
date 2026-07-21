from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from database.connection import get_db as get_db_session
from core.security import get_current_user_from_token
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


def get_household_id(current_user: dict) -> str:
    """Extract the household ID from the current user.

    Raises HTTPException 400 if the user is not attached to a household.
    """
    household_id = current_user["user"].households[0].id if current_user["user"].households else None
    if not household_id:
        raise HTTPException(status_code=400, detail="User is not attached to a household")
    return household_id

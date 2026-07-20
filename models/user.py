from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from database.connection import Base
from models.base import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_fake_login = Column(Boolean, default=False, nullable=False)
    google_sub = Column(String(255), unique=True, nullable=True, index=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

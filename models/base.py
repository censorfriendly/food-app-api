from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, DateTime, func

from database.connection import Base


class TimestampMixin:
    """Adds created_at and updated_at columns to a model."""

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SoftDeleteMixin:
    """Adds is_deleted and deleted_at columns for soft deletes."""

    is_deleted = Column(String(1), default="0", nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

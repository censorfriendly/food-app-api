from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Query, Session, sessionmaker

from config.settings import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


class FilteredSession(Session):
    """Session that automatically excludes soft-deleted records from all queries.

    Any model inheriting from SoftDeleteMixin will have `is_deleted == False`
    appended to its WHERE clause automatically.

    To intentionally include deleted records, pass `include_deleted=True`:
        session = SessionLocal(include_deleted=True)
    """

    def __init__(self, *args, include_deleted: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self._include_deleted = include_deleted

    def query(self, *args, **kwargs) -> Query:
        # Lazy import to prevent circular dependency with models/__init__.py
        from models.base import SoftDeleteMixin

        query = super().query(*args, **kwargs)
        if self._include_deleted:
            return query

        # Add soft-delete filter for any model that uses SoftDeleteMixin
        for desc in query.column_descriptions:
            model = desc.get("type")
            if model and issubclass(model, SoftDeleteMixin):
                query = query.filter(model.is_deleted.is_(False))
        return query


SessionLocal = sessionmaker(bind=engine, class_=FilteredSession, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_include_deleted():
    """Session that includes soft-deleted records (for admin/audit queries)."""
    db = SessionLocal(include_deleted=True)
    try:
        yield db
    finally:
        db.close()

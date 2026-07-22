from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

from database.connection import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """Abstract repository with shared CRUD behavior for all domain repositories."""

    def __init__(self, model: type[ModelType], db: Session):
        self.model = model
        self.db = db

    @property
    @abstractmethod
    def model_type(self) -> type[ModelType]:
        """Return the SQLAlchemy model class used by this repository."""
        raise NotImplementedError

    def get_by_id(self, id: Any) -> ModelType | None:
        return self.db.query(self.model_type).filter(self.model_type.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return self.db.query(self.model_type).offset(skip).limit(limit).all()

    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: Any, values: dict) -> ModelType | None:
        obj = self.get_by_id(id)
        if obj:
            for key, value in values.items():
                setattr(obj, key, value)
            self.db.commit()
            self.db.refresh(obj)
        return obj

    def delete(self, id: Any) -> bool:
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

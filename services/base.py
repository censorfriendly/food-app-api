from abc import ABC
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from repositories.base import BaseRepository

ServiceModelType = TypeVar("ServiceModelType")


class BaseService(ABC, Generic[ServiceModelType]):
    """Abstract service with shared database/session access for domain services."""

    def __init__(self, db: Session):
        self.db = db

    @property
    def repository(self) -> BaseRepository[ServiceModelType]:
        raise NotImplementedError

from typing import Any

from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict[str, str] | None = None


class PaginatedResponse(BaseModel):
    success: bool = True
    data: list[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20

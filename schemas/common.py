from typing import Optional, Any, Dict
from pydantic import BaseModel


class SuccessResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: Optional[Dict[str, str]] = None


class PaginatedResponse(BaseModel):
    success: bool = True
    data: list[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20

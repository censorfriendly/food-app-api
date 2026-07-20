from fastapi import HTTPException


class AppError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str):
        detail = {"code": code, "message": message}
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(status_code=404, code="NOT_FOUND", message=message)


class AuthenticationError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(status_code=401, code="UNAUTHORIZED", message=message)


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(status_code=400, code="VALIDATION_ERROR", message=message)


class ConflictError(AppError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(status_code=409, code="CONFLICT", message=message)

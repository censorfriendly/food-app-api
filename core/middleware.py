import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from utils.logger import setup_logger

logger = setup_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log request method, path, status code, and duration."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()

        response = await call_next(request)

        duration_ms = (time.time() - start) * 1000
        logger.info(
            "%s %s %s %.2fms",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response

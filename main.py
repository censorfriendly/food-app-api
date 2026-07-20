from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import get_settings
from core.middleware import LoggingMiddleware
from exceptions.custom import AppError
from schemas.common import ErrorResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - create tables if they don't exist
    from database.connection import Base, engine
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler for custom errors
@app.exception_handler(AppError)
async def app_error_handler(request, exc):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail).model_dump(),
    )

# Mount routers
from routers import health, auth, items

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(items.router)

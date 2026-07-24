from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import get_settings
from core.middleware import LoggingMiddleware
from database.connection import Base, engine
from exceptions.custom import AppError

# Mount routers
from routers import (
    auth,
    health,
    households,
    ingredients,
    planned_meals,
    recipe_ingredients,
    recipes,
    shopping_lists,
    weekly_plans,
)
from schemas.common import ErrorResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schema changes belong in Alembic migrations, not application startup.

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
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail).model_dump(),
    )


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(households.router)
app.include_router(recipes.router)
app.include_router(ingredients.router)
app.include_router(recipe_ingredients.router)
app.include_router(weekly_plans.router)
app.include_router(planned_meals.router)
app.include_router(shopping_lists.router)

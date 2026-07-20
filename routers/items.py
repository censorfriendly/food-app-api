from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from core.deps import DbSession
from schemas.common import SuccessResponse

router = APIRouter(prefix="/api/v1/items", tags=["Items"])


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class ItemOut(BaseModel):
    name: str
    description: Optional[str] = None


@router.get("", response_model=SuccessResponse)
async def get_items(db: DbSession):
    return SuccessResponse(data={"items": []})


@router.post("", response_model=SuccessResponse, status_code=201)
async def create_item(item: ItemCreate, db: DbSession):
    if not item.name.strip():
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    return SuccessResponse(data={"name": item.name, "description": item.description})

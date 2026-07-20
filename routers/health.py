from fastapi import APIRouter

from schemas.common import SuccessResponse

router = APIRouter(tags=["Health"])


@router.get("/api/v1/health", response_model=SuccessResponse)
async def health_check():
    return SuccessResponse(data={"status": "healthy"})

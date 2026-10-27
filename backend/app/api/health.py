from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthOut(BaseModel):
    status: Literal["ok"]


@router.get("/health", response_model=HealthOut, status_code=200)
async def health() -> HealthOut:
    return HealthOut(status="ok")

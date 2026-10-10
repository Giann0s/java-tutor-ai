from fastapi import APIRouter, HTTPException
from starlette import status

from app.api.dependencies import db_dependency, professor_dependency
from app.schemas.statistics_schemas import ClassOverviewResponse
from app.services import statistics_service

router = APIRouter(
    prefix="/statistics",
    tags=["statistics"]
)


@router.get("/class-overview", status_code=status.HTTP_200_OK, response_model=ClassOverviewResponse)
async def get_class_overview(db: db_dependency, professor: professor_dependency):
    return statistics_service.get_class_overview(db)


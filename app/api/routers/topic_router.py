from fastapi import APIRouter, HTTPException
from starlette import status

from app.api.dependencies import db_dependency, professor_dependency
from app.schemas.topic_schemas import TopicResponse, CreateTopic, UpdateTopic
from app.services import topic_service

router = APIRouter(
    prefix="/topics",
    tags=["topic"]
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[TopicResponse])
async def get_topics(db: db_dependency):
    return topic_service.get_all_topics(db)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TopicResponse)
async def create_new_topic(db: db_dependency, professor: professor_dependency, new_topic: CreateTopic):
    new_topic_model = topic_service.create_topic(db, new_topic)
    if not new_topic_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Το συγκεκριμένο topic υπάρχει ήδη."
        )
    return new_topic_model


@router.patch("/{topic_id}", status_code=status.HTTP_200_OK, response_model=TopicResponse)
async def update_topic(db: db_dependency, professor: professor_dependency, topic_id: int, updated_data: UpdateTopic):
    updated_topic_model = topic_service.update_topic(db, topic_id, updated_data)
    if not updated_topic_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Δεν βρέθηκε το συγκεκριμένο topic."
        )
    return updated_topic_model


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(db: db_dependency, professor: professor_dependency, topic_id: int):
    deleted_topic = topic_service.delete_topic(db, topic_id)
    if not deleted_topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Δεν βρέθηκε το συγκεκριμένο topic."
        )


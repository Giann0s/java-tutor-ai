from fastapi import APIRouter, HTTPException
from starlette import status

from app.api.dependencies import db_dependency, student_dependency
from app.schemas.chat_schemas import ConversationResponse, ChatRequest
from app.services import chat_service

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ConversationResponse)
async def llm_chat(db: db_dependency, student: student_dependency, request: ChatRequest):
    ai_response = chat_service.process_student_message(db, student.id, request.conversation_id, request.user_text)
    if ai_response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Δεν βρέθηκε συζήτηση με τα συγκεκριμένα στοιχεία."
        )
    if not ai_response:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Υπήρξε πρόβλημα στην επικοινωνία με το LLM."
        )
    return ai_response

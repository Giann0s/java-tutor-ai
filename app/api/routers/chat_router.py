from fastapi import APIRouter, HTTPException, BackgroundTasks
from starlette import status

from app.api.dependencies import db_dependency, student_dependency
from app.schemas.chat_schemas import ConversationResponse, ChatRequest
from app.services import chat_service
from app.services.student_mastery_service import calculate_mastery_code_feedback

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ConversationResponse)
async def llm_chat(db: db_dependency,
                   student: student_dependency,
                   request: ChatRequest,
                   background_tasks: BackgroundTasks):
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

    if ai_response.get("topic_id") and ai_response.get("severity"):
        background_tasks.add_task(
            calculate_mastery_code_feedback,
            db=db,
            user_id=student.id,
            topic_id=ai_response["topic_id"],
            severity=ai_response["severity"],
            source_id=ai_response["ai_message_id"]
        )

    return ConversationResponse(
        conversation_id=ai_response["conversation_id"],
        title=ai_response["title"],
        ai_response=ai_response["ai_response"]
    )

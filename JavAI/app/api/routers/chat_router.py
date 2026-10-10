from fastapi import APIRouter, HTTPException, BackgroundTasks
from starlette import status

from app.api.dependencies import db_dependency, student_dependency, professor_dependency, user_dependency
from app.schemas.chat_schemas import ConversationResponse, ChatRequest, ConversationHistory, ConversationMessage
from app.services import chat_service
from app.services.student_mastery_service import calculate_mastery_code_feedback

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ConversationResponse)
async def llm_chat_student(db: db_dependency,
                           student: student_dependency,
                           request: ChatRequest,
                           background_tasks: BackgroundTasks):
    try:
        ai_response = chat_service.process_chat_message(db, student.id, request.conversation_id, request.user_text,
                                                        False)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

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

    # Χρήση των background tasks για υπολογισμό του mastery
    # για να μην καθυστερεί η επιστροφή της απάντησης στον χρήστη.
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


@router.post("/professor", status_code=status.HTTP_201_CREATED, response_model=ConversationResponse)
async def llm_chat_professor(db: db_dependency,
                             professor: professor_dependency,
                             request: ChatRequest):
    try:
        ai_response = chat_service.process_chat_message(db, professor.id, request.conversation_id, request.user_text,
                                                        True)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

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

    return ConversationResponse(
        conversation_id=ai_response["conversation_id"],
        title=ai_response["title"],
        ai_response=ai_response["ai_response"]
    )


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ConversationHistory])
async def get_all_conversations(db: db_dependency, user: user_dependency):
    return chat_service.get_conversations(db, user.id)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(db: db_dependency, user: user_dependency, conversation_id: int):
    deleted_conversation = chat_service.delete_conversation(db, user.id, conversation_id)
    if not deleted_conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Δεν βρέθηκε η συγκεκριμένη συζήτηση."
        )


@router.get("/{conversation_id}/messages", status_code=status.HTTP_200_OK, response_model=list[ConversationMessage])
async def get_conversation_messages(db: db_dependency, user: user_dependency, conversation_id: int):
    return chat_service.get_messages_per_conversation(db, conversation_id, user.id)




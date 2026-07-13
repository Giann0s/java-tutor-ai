import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.chat import Conversation, Message
from app.services import llm_service


def process_student_message(db: Session, user_id: int, conversation_id: int, user_text: str):
    if conversation_id == 0:
        dynamic_title = user_text[:35] + "..." if len(user_text) > 35 else user_text

        conversation = Conversation(
            title=dynamic_title,
            user_id=user_id,
            created_at=datetime.now()
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    else:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

        if not conversation:
            return None

    previous_messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at.asc()).all()

    user_message = Message(
        conversation_id=conversation.id,
        sender_role="user",
        content=user_text,
        created_at=datetime.now()
    )

    db.add(user_message)
    db.commit()

    try:
        ai_response_text = llm_service.llm_chat(
            new_message=user_text,
            db_messages=previous_messages,
        )
    except Exception as e:
        logging.error(f"LLM Error: {str(e)}")
        return False

    ai_message = Message(
        conversation_id=conversation.id,
        sender_role="model",
        content=ai_response_text,
        created_at=datetime.now()
    )
    db.add(ai_message)
    db.commit()

    return {
        "conversation_id": conversation.id,
        "title": conversation.title,
        "ai_response": ai_response_text
    }



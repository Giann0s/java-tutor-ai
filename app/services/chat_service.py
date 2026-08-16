import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.chat import Conversation, Message
from app.models.user import Topic
from app.services import llm_service


def process_chat_message(db: Session, user_id: int, conversation_id: int, user_text: str, is_professor: bool = False):
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
        if is_professor:
            ai_output = llm_service.llm_chat_professor(
                new_message=user_text,
                db_messages=previous_messages
            )
        else:
            # Παίρνουμε τα topics απο τη βάση ώστε να γνωρίζει πως να κάνει
            # τις αντιστοιχίσεις το LLM.
            all_topics = db.query(Topic).all()
            topics_string = ""
            for t in all_topics:
                topics_string += f"{t.id}: {t.name} ({t.description})\n"

            ai_output = llm_service.llm_chat(
                new_message=user_text,
                db_messages=previous_messages,
                dynamic_topics=topics_string
            )
    except Exception as e:
        logging.error(f"LLM Error: {str(e)}")
        return False

    ai_message = Message(
        conversation_id=conversation.id,
        sender_role="model",
        content=ai_output.reply,
        created_at=datetime.now()
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    return {
        "conversation_id": conversation.id,
        "title": conversation.title,
        "ai_response": ai_output.reply,
        "topic_id": ai_output.topic_id,
        "severity": ai_output.severity,
        "ai_message_id": ai_message.id
    }


def get_conversations(db: Session, user_id: int):
    return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.created_at.desc()).all()


def delete_conversation(db: Session, user_id: int, conversation_id: int):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()

    if not conversation:
        return False

    db.delete(conversation)
    db.commit()
    return True

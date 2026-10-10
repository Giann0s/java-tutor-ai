from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ChatRequest(BaseModel):
    conversation_id: int = Field(default=0)
    user_text: str = Field(min_length=1)


class ConversationResponse(BaseModel):
    conversation_id: int
    title: str
    ai_response: str


class LLMOutput(BaseModel):
    reply: str
    topic_id: Optional[int] = None
    severity: Optional[str] = None


class ConversationHistory(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class ConversationMessage(BaseModel):
    id: int
    sender_role: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


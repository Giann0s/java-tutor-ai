from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: int = Field(default=0)
    user_text: str = Field(min_length=1)


class ConversationResponse(BaseModel):
    conversation_id: str
    title: str
    ai_response: str

from pydantic import BaseModel, ConfigDict, Field


class CreateTopic(BaseModel):
    name: str = Field(min_length=3)
    description: str = Field(min_length=10)


class UpdateTopic(BaseModel):
    description: str = Field(min_length=10)


class TopicResponse(BaseModel):
    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)
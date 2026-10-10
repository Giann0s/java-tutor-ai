from pydantic import BaseModel


class TopicAverage(BaseModel):
    topic_id: int
    topic_name: str
    average_mastery: float


class ClassOverviewResponse(BaseModel):
    topics: list[TopicAverage]

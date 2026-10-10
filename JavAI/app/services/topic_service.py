from sqlalchemy.orm import Session

from app.models.user import Topic
from app.schemas.topic_schemas import CreateTopic, UpdateTopic


def get_all_topics(db: Session):
    return db.query(Topic).all()


def create_topic(db: Session, new_topic: CreateTopic):
    existing_topic = db.query(Topic).filter(Topic.name == new_topic.name).first()
    if existing_topic:
        return False

    new_topic_model = Topic(
        name=new_topic.name,
        description=new_topic.description
    )

    db.add(new_topic_model)
    db.commit()
    db.refresh(new_topic_model)
    return new_topic_model


# Ενημερώνει μόνο το description του topic
def update_topic(db: Session, topic_id: int, updated_data: UpdateTopic):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        return False

    topic.description = updated_data.description
    db.commit()
    db.refresh(topic)
    return topic


def delete_topic(db: Session, topic_id: int):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        return False

    db.delete(topic)
    db.commit()
    return True

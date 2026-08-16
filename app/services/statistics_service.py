from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import Topic, StudentMastery


def get_class_overview(db: Session):
    results = db.query(
        Topic.id.label("topic_id"),
        Topic.name.label("topic_name"),
        func.avg(StudentMastery.mastery_level).label("avg_mastery")
    ).outerjoin( # Χρήση outerjoin για να φέρει όλα τα topics, ακόμα και αν δεν υπάρχει καταχώρηση στο StudentMastery
        StudentMastery, Topic.id == StudentMastery.topic_id
    ).group_by(
        Topic.id, Topic.name
    ).all()

    topics_out = []

    for row in results:
        avg_val = float(row.avg_mastery) if row.avg_mastery is not None else 0.0

        topics_out.append({
            "topic_id": row.topic_id,
            "topic_name": row.topic_name,
            "average_mastery": avg_val
        })

    return {
        "topics": topics_out
    }

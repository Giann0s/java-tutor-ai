from sqlalchemy.orm import Session, joinedload

from app.models.attempt import ExerciseAttempt, StudentAnswer
from app.models.user import StudentMastery, MasteryLog


# Υπολογίζει mastery με βάση τις επιδόσεις του φοιτητή στις ασκήσεις
def calculate_mastery_exercise(db: Session, exercise_attempt_id: int):
    exercise = db.query(ExerciseAttempt).options(
        joinedload(ExerciseAttempt.student_answers).joinedload(StudentAnswer.question)
    ).filter(ExerciseAttempt.id == exercise_attempt_id).first()

    if not exercise:
        return None

    topic_scores = {}

    for answer in exercise.student_answers:
        topic_id = answer.question.topic_id
        if not topic_id:
            continue

        if topic_id not in topic_scores:
            topic_scores[topic_id] = {
                "earned_points": 0.0,
                "total_points": 0.0
            }

        topic_scores[topic_id]["earned_points"] += answer.score_awarded or 0.0
        topic_scores[topic_id]["total_points"] += answer.question.points or 0.0

    alpha = 0.3  # Smoothing factor
    for topic_id, scores in topic_scores.items():
        earned = scores["earned_points"]
        total = scores["total_points"]

        score = (earned / total) if total > 0 else 0.0

        student_mastery = db.query(StudentMastery).filter(
            StudentMastery.user_id == exercise.user_id,
            StudentMastery.topic_id == topic_id
        ).first()

        if student_mastery:
            old_mastery = student_mastery.mastery_level
            new_mastery = (alpha * score) + ((1 - alpha) * old_mastery)  # Εφαρμογή EMA
            student_mastery.mastery_level = new_mastery
        else:
            # Cold start: αφού δεν υπάρχει παλιό mastery, μπαίνει το ίδιο το score
            old_mastery = 0.0
            new_mastery = score

            student_mastery = StudentMastery(
                user_id=exercise.user_id,
                topic_id=topic_id,
                mastery_level=new_mastery
            )
            db.add(student_mastery)

        mastery_log = MasteryLog(
            user_id=exercise.user_id,
            topic_id=topic_id,
            old_mastery=old_mastery,
            new_mastery=new_mastery,
            source=f"EXERCISE_ATTEMPT_{exercise_attempt_id}"
        )

        db.add(mastery_log)
    db.commit()


# Υπολογίζει mastery με βάση τους κώδικες που στέλνει ο φοιτητής για feedback
def calculate_mastery_code_feedback(db: Session, user_id: int, topic_id: int, severity: str, source_id: int):
    print(
        f"DEBUG INPUTS -> user_id: {user_id}, topic_id: {topic_id}, severity: {severity} (type: {type(severity)}), source_id: {source_id}")
    severity_to_score = {
        "LOW": 0.7,
        "MEDIUM": 0.4,
        "HIGH": 0.0,
        "PERFECT": 1.0
    }

    score = severity_to_score.get(severity.upper(), 0.5)
    alpha = 0.05  # Μικρότερη βαρύτητα σε σχέση με τις ασκήσεις

    student_mastery = db.query(StudentMastery).filter(
        StudentMastery.user_id == user_id,
        StudentMastery.topic_id == topic_id
    ).first()

    if student_mastery:
        old_mastery = student_mastery.mastery_level
        new_mastery = (alpha * score) + ((1 - alpha) * old_mastery)
        student_mastery.mastery_level = new_mastery
    else:
        old_mastery = 0.0
        new_mastery = score

        student_mastery = StudentMastery(
            user_id=user_id,
            topic_id=topic_id,
            mastery_level=new_mastery
        )
        db.add(student_mastery)

    mastery_log = MasteryLog(
        user_id=user_id,
        topic_id=topic_id,
        old_mastery=old_mastery,
        new_mastery=new_mastery,
        source=f"CHAT_CONVERSATION_{source_id}"
    )

    db.add(mastery_log)
    db.commit()
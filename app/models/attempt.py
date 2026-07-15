from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class ExerciseAttempt(Base):
    __tablename__ = "exercise_attempt"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_id = Column(Integer, ForeignKey("exercise.id"))
    status = Column(String)
    total_score = Column(Integer)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="exercise_attempts")
    exercise = relationship("Exercise", back_populates="exercise_attempts")
    student_answers = relationship("StudentAnswer", back_populates="exercise_attempt", cascade="all, delete-orphan")


class StudentAnswer(Base):
    __tablename__ = "student_answer"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("exercise_attempt.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    provided_answer = Column(Text)
    is_correct = Column(Boolean)
    llm_feedback = Column(Text)
    score_awarded = Column(Integer)

    exercise_attempt = relationship("ExerciseAttempt", back_populates="student_answers")
    question = relationship("Question", back_populates="student_answers")
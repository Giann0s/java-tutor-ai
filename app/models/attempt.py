from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempt"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quiz.id"))
    status = Column(String)
    total_score = Column(Integer)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="quiz_attempts")
    student_answers = relationship("StudentAnswer", back_populates="quiz_attempt", cascade="all, delete-orphan")


class StudentAnswer(Base):
    __tablename__ = "student_answer"

    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempt.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    provided_answer = Column(Text)
    is_correct = Column(Boolean)
    llm_feedback = Column(Text)
    score_awarded = Column(Integer)

    quiz_attempt = relationship("QuizAttempt", back_populates="student_answers")
    question = relationship("Question", back_populates="student_answers")
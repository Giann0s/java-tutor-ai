from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float, func
from sqlalchemy.orm import relationship

from app.db.database import Base


# Πίνακας χρηστών
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    role = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    masteries = relationship("StudentMastery", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="teacher", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")


# Πίνακας θεμάτων σχετικά με τη Java
class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)

    masteries = relationship("StudentMastery", back_populates="topic", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="topic", cascade="all, delete-orphan")


# Πίνακας που δείχνει το ποσοστό κατανοήσης των φοιτητών
class StudentMastery(Base):
    __tablename__ = "student_mastery"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    mastery_level = Column(Float)  # ποσοστό κατανόησης
    needs_review = Column(Boolean)
    last_assessed_at = Column(DateTime)

    user = relationship("User", back_populates="masteries")
    topic = relationship("Topic", back_populates="masteries")

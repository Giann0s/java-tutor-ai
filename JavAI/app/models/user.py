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
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    masteries = relationship("StudentMastery", back_populates="user", cascade="all, delete-orphan")
    mastery_log = relationship("MasteryLog", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    exercises = relationship("Exercise", back_populates="creator", cascade="all, delete-orphan")
    exercise_attempts = relationship("ExerciseAttempt", back_populates="user", cascade="all, delete-orphan")


# Πίνακας θεμάτων σχετικά με τη Java
class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)

    masteries = relationship("StudentMastery", back_populates="topic", cascade="all, delete-orphan")
    mastery_log = relationship("MasteryLog", back_populates="topic", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="topic", cascade="all, delete-orphan")


# Πίνακας που δείχνει το ποσοστό κατανοήσης των φοιτητών
class StudentMastery(Base):
    __tablename__ = "student_mastery"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    mastery_level = Column(Float)  # ποσοστό κατανόησης

    user = relationship("User", back_populates="masteries")
    topic = relationship("Topic", back_populates="masteries")


# Πίνακας που κρατάει το ιστορικό του mastery ανά φοιτητή
class MasteryLog(Base):
    __tablename__ = "mastery_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    old_mastery = Column(Float)
    new_mastery = Column(Float)
    source = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="mastery_log")
    topic = relationship("Topic", back_populates="mastery_log")

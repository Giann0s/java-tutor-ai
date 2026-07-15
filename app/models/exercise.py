from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


# Πίνακας για τις ασκήσεις που κάνει generate ο καθηγητής ή ένας μαθητής
class Exercise(Base):
    __tablename__ = "exercise"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    keywords = Column(String, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    is_practice = Column(Boolean, default=False)  # ελέγχει αν είναι επίσημη εξέταση/άσκηση από τον καθηγητή ή όχι
    created_at = Column(DateTime)

    creator = relationship("User", back_populates="exercises")
    questions = relationship("Question", back_populates="exercise", cascade="all, delete-orphan")
    exercise_attempts = relationship("ExerciseAttempt", back_populates="exercise", cascade="all, delete-orphan")


# Πίνακας για τις ερωτήσεις/ζητούμενα μιας άσκησης
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercise.id"), nullable=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    question_type = Column(String)  # Είδος ερώτησης (πολλαπλής, συγγραφή κώδικα)
    content = Column(Text)
    correct_answer = Column(Text)  # Ενδεικτική σωστή απάντηση
    points = Column(Integer)
    is_generated_by_llm = Column(Boolean)

    exercise = relationship("Exercise", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    choices = relationship("Choice", back_populates="question", cascade="all, delete-orphan")
    student_answers = relationship("StudentAnswer", back_populates="question", cascade="all, delete-orphan")


# Πίνακας για τις επιλογές που δίνονται ως πιθανές απαντήσεις
# (αν η άσκηση είναι πολλαπλής επιλογής)
class Choice(Base):
    __tablename__ = "choices"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    text = Column(String)
    is_correct = Column(Boolean)

    question = relationship("Question", back_populates="choices")

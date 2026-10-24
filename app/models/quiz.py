from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    professor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    topic = Column(String(255))
    time_limit = Column(Integer, nullable=False)  # in minutes
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    randomize_questions = Column(Boolean, default=False)
    randomize_options = Column(Boolean, default=False)
    max_attempts = Column(Integer, default=1)
    show_immediate_results = Column(Boolean, default=True)
    show_correct_answers = Column(Boolean, default=True)
    show_explanations = Column(Boolean, default=True)
    passing_percentage = Column(Integer, default=60)
    quiz_code = Column(String(20), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    professor = relationship("User", back_populates="professor_quizzes", foreign_keys=[professor_id])
    quiz_questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    question_order = Column(Integer, nullable=False)
    marks = Column(Integer, default=1)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="quiz_questions")
    question = relationship("Question", back_populates="quiz_questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    submitted_at = Column(DateTime(timezone=True))
    time_taken = Column(Integer)  # in seconds
    score = Column(Integer)
    percentage = Column(Numeric(5, 2))
    status = Column(String(20), default="in_progress")  # in_progress, submitted, timed_out
    attempt_number = Column(Integer, default=1)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("User", back_populates="quiz_attempts")
    student_answers = relationship("StudentAnswer", back_populates="attempt", cascade="all, delete-orphan")
    result = relationship("Result", back_populates="attempt", uselist=False)


class StudentAnswer(Base):
    __tablename__ = "student_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    answer = Column(Text)
    is_correct = Column(Boolean)
    time_spent = Column(Integer)  # in seconds
    answered_at = Column(DateTime(timezone=True))
    
    # Relationships
    attempt = relationship("QuizAttempt", back_populates="student_answers")
    question = relationship("Question", back_populates="student_answers")


class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempts.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    wrong_answers = Column(Integer, nullable=False)
    unanswered = Column(Integer, nullable=False)
    total_marks = Column(Integer, nullable=False)
    obtained_marks = Column(Integer, nullable=False)
    percentage = Column(Numeric(5, 2), nullable=False)
    passed = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    attempt = relationship("QuizAttempt", back_populates="result")

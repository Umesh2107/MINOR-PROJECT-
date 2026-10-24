from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(Integer, ForeignKey("study_materials.id", ondelete="SET NULL"), nullable=True)
    topic = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # MCQ, True/False, Fill in the Blank, Short Answer, Descriptive
    difficulty = Column(String(20), nullable=False)  # Easy, Medium, Hard
    style = Column(String(50), nullable=False)  # Normal, Conceptual, Twisted, Scenario-Based, Application-Based
    options = Column(JSON)  # Array of options for MCQ
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)
    is_validated = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="questions")
    material = relationship("StudyMaterial", back_populates="questions")
    quiz_questions = relationship("QuizQuestion", back_populates="question")
    question_bank_entries = relationship("QuestionBank", back_populates="question")
    student_answers = relationship("StudentAnswer", back_populates="question")


class QuestionBank(Base):
    __tablename__ = "question_bank"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="question_bank")
    question = relationship("Question", back_populates="question_bank_entries")

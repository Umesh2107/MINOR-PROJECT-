from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime


class QuestionBase(BaseModel):
    topic: str = Field(..., min_length=1, max_length=255)
    question: str = Field(..., min_length=1)
    type: str = Field(..., description="MCQ, True/False, Fill in the Blank, Short Answer, Descriptive")
    difficulty: str = Field(..., description="Easy, Medium, Hard")
    style: str = Field(..., description="Normal, Conceptual, Twisted, Scenario-Based, Application-Based")
    options: Optional[List[str]] = None
    correct_answer: str = Field(..., min_length=1)
    explanation: Optional[str] = None


class QuestionCreate(QuestionBase):
    material_id: Optional[int] = None


class QuestionUpdate(BaseModel):
    topic: Optional[str] = Field(None, min_length=1, max_length=255)
    question: Optional[str] = Field(None, min_length=1)
    type: Optional[str] = None
    difficulty: Optional[str] = None
    style: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = Field(None, min_length=1)
    explanation: Optional[str] = None
    is_approved: Optional[bool] = None


class Question(QuestionBase):
    id: int
    user_id: int
    material_id: Optional[int] = None
    is_validated: bool
    is_approved: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class QuestionGenerationRequest(BaseModel):
    topic: Optional[str] = Field(None, min_length=1, max_length=255)
    material_id: Optional[int] = None
    material_only: bool = False
    num_questions: int = Field(10, ge=1, le=50)
    question_type: str = Field("MCQ", description="MCQ, True/False, Fill in the Blank, Short Answer, Descriptive, Mixed")
    difficulty: str = Field("Medium", description="Easy, Medium, Hard, Mixed")
    style: str = Field("Normal", description="Normal, Conceptual, Twisted, Scenario-Based, Application-Based, Mixed")


class QuestionValidationRequest(BaseModel):
    question_id: int


class QuestionRegenerationRequest(BaseModel):
    question_id: int
    new_params: Optional[dict] = None


class QuestionBankRequest(BaseModel):
    question_id: int


class QuestionBankItem(BaseModel):
    id: int
    question: Question
    added_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

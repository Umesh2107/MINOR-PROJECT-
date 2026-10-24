from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


class QuizBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    topic: Optional[str] = Field(None, max_length=255)
    time_limit: int = Field(..., ge=1)  # in minutes
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    randomize_questions: bool = False
    randomize_options: bool = False
    max_attempts: int = Field(1, ge=1)
    show_immediate_results: bool = True
    show_correct_answers: bool = True
    show_explanations: bool = True
    passing_percentage: int = Field(60, ge=0, le=100)


class QuizCreate(QuizBase):
    question_ids: List[int] = Field(..., min_items=1)


class QuizUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    topic: Optional[str] = Field(None, max_length=255)
    time_limit: Optional[int] = Field(None, ge=1)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    randomize_questions: Optional[bool] = None
    randomize_options: Optional[bool] = None
    max_attempts: Optional[int] = Field(None, ge=1)
    show_immediate_results: Optional[bool] = None
    show_correct_answers: Optional[bool] = None
    show_explanations: Optional[bool] = None
    passing_percentage: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class Quiz(QuizBase):
    id: int
    professor_id: int
    quiz_code: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class QuizWithQuestions(Quiz):
    questions: List[dict]


class QuizQuestionBase(BaseModel):
    question_id: int
    question_order: int = Field(..., ge=1)
    marks: int = Field(1, ge=1)


class QuizQuestionCreate(QuizQuestionBase):
    quiz_id: int


class QuizQuestion(QuizQuestionBase):
    id: int
    quiz_id: int
    
    model_config = ConfigDict(from_attributes=True)


class QuizAttemptBase(BaseModel):
    quiz_id: int


class QuizAttemptCreate(QuizAttemptBase):
    pass


class QuizAttemptSubmit(BaseModel):
    attempt_id: int
    answers: List[dict]


class QuizAttempt(QuizAttemptBase):
    id: int
    student_id: int
    started_at: datetime
    submitted_at: Optional[datetime] = None
    time_taken: Optional[int] = None
    score: Optional[int] = None
    percentage: Optional[Decimal] = None
    status: str
    attempt_number: int
    
    model_config = ConfigDict(from_attributes=True)


class StudentAnswerBase(BaseModel):
    question_id: int
    answer: str


class StudentAnswer(StudentAnswerBase):
    id: int
    attempt_id: int
    is_correct: Optional[bool] = None
    time_spent: Optional[int] = None
    answered_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ResultBase(BaseModel):
    total_questions: int
    correct_answers: int
    wrong_answers: int
    unanswered: int
    total_marks: int
    obtained_marks: int
    percentage: Decimal
    passed: bool


class Result(ResultBase):
    id: int
    attempt_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class QuizJoinRequest(BaseModel):
    quiz_code: str = Field(..., min_length=1, max_length=20)

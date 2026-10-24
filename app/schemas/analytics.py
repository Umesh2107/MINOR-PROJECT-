from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class ProfessorOverview(BaseModel):
    total_quizzes: int
    active_quizzes: int
    completed_quizzes: int
    total_students: int
    average_score: Optional[Decimal] = None
    highest_score: Optional[Decimal] = None
    lowest_score: Optional[Decimal] = None


class QuizAnalytics(BaseModel):
    quiz_id: int
    quiz_title: str
    total_attempts: int
    average_score: Optional[Decimal] = None
    highest_score: Optional[Decimal] = None
    lowest_score: Optional[Decimal] = None
    pass_rate: Optional[Decimal] = None
    average_time: Optional[int] = None
    score_distribution: Dict[str, int]
    most_difficult_questions: List[dict]
    most_incorrect_questions: List[dict]
    topic_wise_performance: Dict[str, dict]


class StudentPerformance(BaseModel):
    student_id: int
    student_name: str
    score: int
    total_marks: int
    percentage: Decimal


class QuizStudentResults(BaseModel):
    quiz_id: int
    quiz_title: str
    students: List[StudentPerformance]


class StudentOverview(BaseModel):
    total_quizzes_attempted: int
    average_percentage: Optional[Decimal] = None
    highest_percentage: Optional[Decimal] = None
    lowest_percentage: Optional[Decimal] = None
    strong_topics: List[str]
    weak_topics: List[str]
    total_questions_answered: int
    correct_answers: int
    accuracy: Optional[Decimal] = None


class StudentPerformanceRecord(BaseModel):
    topic: str
    total_quizzes: int
    total_questions: int
    correct_answers: int
    average_score: Optional[Decimal] = None
    strength: Optional[List[str]] = None
    weakness: Optional[List[str]] = None
    last_updated: datetime


class StudentPerformanceTrend(BaseModel):
    quiz_title: str
    date: datetime
    percentage: Decimal
    time_taken: Optional[int] = None


class AIFeedback(BaseModel):
    feedback: str
    strong_areas: List[str]
    weak_areas: List[str]
    recommendations: List[str]

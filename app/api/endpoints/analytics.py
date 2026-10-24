from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.schemas.analytics import (
    ProfessorOverview,
    QuizAnalytics,
    QuizStudentResults,
    StudentOverview,
    StudentPerformanceRecord,
    StudentPerformanceTrend,
    AIFeedback,
)
from app.api.deps import get_current_user, get_current_professor, get_current_student
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/professor/overview", response_model=ProfessorOverview)
def get_professor_overview(
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get professor's dashboard overview."""
    try:
        return AnalyticsService.get_professor_overview(professor_id=current_user.id, db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/professor/quiz/{quiz_id}", response_model=QuizAnalytics)
def get_quiz_analytics(
    quiz_id: int,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a specific quiz."""
    try:
        return AnalyticsService.get_quiz_analytics(quiz_id=quiz_id, db=db)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/professor/quiz/{quiz_id}/students", response_model=QuizStudentResults)
def get_quiz_student_results(
    quiz_id: int,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get student results for a specific quiz."""
    try:
        return AnalyticsService.get_quiz_student_results(quiz_id=quiz_id, db=db)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/student/overview", response_model=StudentOverview)
def get_student_overview(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get student's performance overview."""
    try:
        return AnalyticsService.get_student_overview(student_id=current_user.id, db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/student/performance", response_model=List[StudentPerformanceRecord])
def get_student_performance(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get student's performance records by topic."""
    try:
        return AnalyticsService.get_student_performance_records(student_id=current_user.id, db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/student/trends", response_model=List[StudentPerformanceTrend])
def get_student_performance_trends(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get student's performance trends over time."""
    try:
        return AnalyticsService.get_student_performance_trends(student_id=current_user.id, db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/student/ai-feedback", response_model=AIFeedback)
def get_ai_feedback(
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get AI-generated performance feedback."""
    try:
        return AnalyticsService.generate_ai_feedback(student_id=current_user.id, db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

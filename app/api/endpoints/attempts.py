from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.models.quiz import QuizAttempt as QuizAttemptModel, StudentAnswer as StudentAnswerModel, Result as ResultModel
from app.schemas.quiz import (
    QuizAttempt,
    QuizAttemptCreate,
    QuizAttemptSubmit,
    StudentAnswer,
    Result,
)
from app.api.deps import get_current_user, get_current_student
from app.services.quiz_service import QuizService

router = APIRouter()


@router.post("/start", response_model=QuizAttempt)
def start_quiz_attempt(
    request: QuizAttemptCreate,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Start a quiz attempt."""
    try:
        return QuizService.start_quiz_attempt(
            quiz_id=request.quiz_id,
            student_id=current_user.id,
            db=db
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/submit", response_model=Result)
def submit_quiz_attempt(
    request: QuizAttemptSubmit,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Submit quiz attempt and get results."""
    try:
        return QuizService.submit_quiz_attempt(
            attempt_id=request.attempt_id,
            submission_data=request,
            db=db
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{attempt_id}", response_model=QuizAttempt)
def get_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz attempt details."""
    attempt = db.query(QuizAttemptModel).filter(QuizAttemptModel.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    return attempt


@router.get("/quiz/{quiz_id}", response_model=List[QuizAttempt])
def get_quiz_attempts(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all attempts for a quiz."""
    try:
        return QuizService.get_quiz_attempts(quiz_id=quiz_id, db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{attempt_id}/answers", response_model=List[StudentAnswer])
def get_attempt_answers(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get answers for a quiz attempt."""
    answers = db.query(StudentAnswerModel).filter(StudentAnswerModel.attempt_id == attempt_id).all()
    return answers


@router.get("/{attempt_id}/result", response_model=Result)
def get_attempt_result(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get result for a quiz attempt."""
    result = db.query(ResultModel).filter(ResultModel.attempt_id == attempt_id).first()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")
    return result

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.schemas.quiz import (
    Quiz,
    QuizCreate,
    QuizUpdate,
    QuizWithQuestions,
    QuizJoinRequest,
)
from app.api.deps import get_current_user, get_current_professor, get_current_student
from app.services.quiz_service import QuizService

router = APIRouter()


@router.post("/create", response_model=Quiz)
def create_quiz(
    quiz_data: QuizCreate,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Create a new quiz."""
    try:
        return QuizService.create_quiz(quiz_data=quiz_data, professor_id=current_user.id, db=db)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/my", response_model=List[Quiz])
def get_my_quizzes(
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Get professor's quizzes."""
    try:
        return QuizService.get_professor_quizzes(professor_id=current_user.id, db=db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/code/{quiz_code}", response_model=QuizWithQuestions)
def get_quiz_by_code(
    quiz_code: str,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get quiz by code for students."""
    try:
        quiz = QuizService.get_quiz_by_code(quiz_code=quiz_code, db=db)
        questions_data = QuizService.get_quiz_questions_for_student(quiz_id=quiz.id, db=db)
        # Construct QuizWithQuestions response
        return {
            **quiz.__dict__,
            "questions": questions_data
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/join", response_model=QuizWithQuestions)
def join_quiz(
    request: QuizJoinRequest,
    current_user: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Join a quiz using code."""
    try:
        quiz = QuizService.get_quiz_by_code(quiz_code=request.quiz_code, db=db)
        questions_data = QuizService.get_quiz_questions_for_student(quiz_id=quiz.id, db=db)
        return {
            **quiz.__dict__,
            "questions": questions_data
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{quiz_id}", response_model=QuizWithQuestions)
def get_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz details with questions."""
    try:
        quiz = QuizService.get_quiz(quiz_id=quiz_id, db=db)
        questions_data = QuizService.get_quiz_questions_for_student(quiz_id=quiz.id, db=db)
        return {
            **quiz.__dict__,
            "questions": questions_data
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{quiz_id}", response_model=Quiz)
def update_quiz(
    quiz_id: int,
    quiz_update: QuizUpdate,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Update a quiz."""
    try:
        return QuizService.update_quiz(quiz_id=quiz_id, quiz_update=quiz_update, db=db)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{quiz_id}")
def delete_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Delete a quiz."""
    try:
        QuizService.delete_quiz(quiz_id=quiz_id, db=db)
        return {"message": "Quiz deleted successfully"}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{quiz_id}/publish", response_model=Quiz)
def publish_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Publish a quiz."""
    try:
        return QuizService.publish_quiz(quiz_id=quiz_id, db=db)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

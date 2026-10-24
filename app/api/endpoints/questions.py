from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.user import User
from app.schemas.question import (
    Question,
    QuestionCreate,
    QuestionUpdate,
    QuestionGenerationRequest,
    QuestionValidationRequest,
    QuestionRegenerationRequest,
    QuestionBankRequest,
    QuestionBankItem,
)
from app.api.deps import get_current_user, get_current_professor
from app.services.question_service import QuestionService
from app.services.ai_service import AIService

router = APIRouter()


@router.post("/generate", response_model=List[Question])
def generate_questions(
    request: QuestionGenerationRequest,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Generate questions using AI."""
    try:
        return QuestionService.generate_questions_ai(
            topic=request.topic,
            material_id=request.material_id,
            material_text=getattr(request, "material_text", None),
            material_only=request.material_only,
            num_questions=request.num_questions,
            question_type=request.question_type,
            difficulty=request.difficulty,
            style=request.style,
            user_id=current_user.id,
            db=db
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/validate", response_model=dict)
def validate_question(
    request: QuestionValidationRequest,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Validate a generated question."""
    try:
        return QuestionService.validate_question(request.question_id, db)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/regenerate", response_model=Question)
def regenerate_question(
    request: QuestionRegenerationRequest,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Regenerate a specific question."""
    try:
        return QuestionService.regenerate_question(
            question_id=request.question_id,
            new_params=request.new_params,
            db=db
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/bank", response_model=List[QuestionBankItem])
def get_question_bank(
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db),
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    style: Optional[str] = None,
):
    """Get user's question bank with optional filters."""
    try:
        return QuestionService.get_question_bank(
            user_id=current_user.id,
            db=db,
            topic=topic,
            difficulty=difficulty,
            question_type=question_type,
            style=style
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/bank", response_model=QuestionBankItem)
def add_to_question_bank(
    request: QuestionBankRequest,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Add a question to the question bank."""
    try:
        return QuestionService.add_to_question_bank(
            question_id=request.question_id,
            user_id=current_user.id,
            db=db
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/bank/{bank_id}")
def remove_from_question_bank(
    bank_id: int,
    current_user: User = Depends(get_current_professor),
    db: Session = Depends(get_db)
):
    """Remove a question from the question bank."""
    try:
        QuestionService.remove_from_question_bank(
            bank_id=bank_id,
            user_id=current_user.id,
            db=db
        )
        return {"message": "Successfully removed from question bank"}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{question_id}", response_model=Question)
def get_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific question."""
    try:
        return QuestionService.get_question(question_id, db)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

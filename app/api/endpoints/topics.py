import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.models.topic import Topic as TopicModel
from app.schemas.topic import Topic, TopicSearchRequest, TopicExplanationRequest
from app.api.deps import get_current_user
from app.services.ai_service import AIService

router = APIRouter()


@router.post("/search", response_model=Topic)
def search_topic(
    request: TopicSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search for a topic and save to search history."""
    try:
        explanation = AIService.generate_topic_explanation(request.query)
        content_json = json.dumps(explanation)
        
        topic_entry = TopicModel(
            user_id=current_user.id,
            title=request.query,
            content=content_json
        )
        db.add(topic_entry)
        db.commit()
        db.refresh(topic_entry)
        
        return topic_entry
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/explain", response_model=dict)
def explain_topic(
    request: TopicExplanationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI explanation for a topic."""
    try:
        return AIService.generate_topic_explanation(request.topic)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/history", response_model=List[Topic])
def get_topic_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's topic search history."""
    try:
        topics = db.query(TopicModel).filter(
            TopicModel.user_id == current_user.id
        ).order_by(TopicModel.created_at.desc()).all()
        return topics
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

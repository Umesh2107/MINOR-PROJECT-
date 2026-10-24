from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.models.question import Question, QuestionBank
from app.models.material import StudyMaterial
from app.schemas.question import QuestionCreate, QuestionUpdate
from app.services.ai_service import AIService


class QuestionService:
    """Service for question-related operations."""
    
    @staticmethod
    def create_question(question_data: QuestionCreate, user_id: int, db: Session) -> Question:
        """Create a new question."""
        # Validate material exists if provided
        if question_data.material_id:
            material = db.query(StudyMaterial).filter(
                StudyMaterial.id == question_data.material_id
            ).first()
            if not material:
                raise ValueError("Material not found")
        
        new_question = Question(
            user_id=user_id,
            material_id=question_data.material_id,
            topic=question_data.topic,
            question=question_data.question,
            type=question_data.type,
            difficulty=question_data.difficulty,
            style=question_data.style,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            is_validated=True,
            is_approved=True
        )
        
        db.add(new_question)
        db.commit()
        db.refresh(new_question)
        
        return new_question
    
    @staticmethod
    def get_question(question_id: int, db: Session) -> Question:
        """Get a question by ID."""
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise ValueError("Question not found")
        return question
    
    @staticmethod
    def update_question(question_id: int, question_update: QuestionUpdate, db: Session) -> Question:
        """Update a question."""
        question = QuestionService.get_question(question_id, db)
        
        update_data = question_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(question, field, value)
        
        db.commit()
        db.refresh(question)
        
        return question
    
    @staticmethod
    def delete_question(question_id: int, db: Session) -> bool:
        """Delete a question."""
        question = QuestionService.get_question(question_id, db)
        db.delete(question)
        db.commit()
        return True
    
    @staticmethod
    def generate_questions_ai(
        topic: Optional[str],
        material_id: Optional[int],
        material_text: Optional[str],
        material_only: bool,
        num_questions: int,
        question_type: str,
        difficulty: str,
        style: str,
        user_id: int,
        db: Session
    ) -> List[Question]:
        """Generate questions using AI and save to database."""
        # Get material text if material_id is provided
        if material_id and not material_text:
            material = db.query(StudyMaterial).filter(StudyMaterial.id == material_id).first()
            if material:
                material_text = material.extracted_text
                if not topic:
                    topic = material.title
        
        # Generate questions using AI
        generated_questions = AIService.generate_questions(
            topic=topic,
            material_text=material_text,
            material_only=material_only,
            num_questions=num_questions,
            question_type=question_type,
            difficulty=difficulty,
            style=style
        )
        
        # Save questions to database
        saved_questions = []
        for q_data in generated_questions:
            question_create = QuestionCreate(
                topic=topic or "General",
                question=q_data["question"],
                type=q_data["type"],
                difficulty=q_data["difficulty"],
                style=q_data["style"],
                options=q_data.get("options"),
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation"),
                material_id=material_id
            )
            
            question = QuestionService.create_question(question_create, user_id, db)
            
            # Validate question
            validation_result = AIService.validate_question(q_data)
            question.is_validated = validation_result["is_valid"]
            db.commit()
            
            saved_questions.append(question)
        
        return saved_questions
    
    @staticmethod
    def validate_question(question_id: int, db: Session) -> Dict:
        """Validate a question using AI."""
        question = QuestionService.get_question(question_id, db)
        
        question_data = {
            "question": question.question,
            "type": question.type,
            "difficulty": question.difficulty,
            "style": question.style,
            "options": question.options,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation
        }
        
        validation_result = AIService.validate_question(question_data)
        
        # Update question validation status
        question.is_validated = validation_result["is_valid"]
        db.commit()
        
        return validation_result
    
    @staticmethod
    def regenerate_question(question_id: int, new_params: Optional[Dict], db: Session) -> Question:
        """Regenerate a question using AI."""
        question = QuestionService.get_question(question_id, db)
        
        original_question_data = {
            "question": question.question,
            "type": question.type,
            "difficulty": question.difficulty,
            "style": question.style,
            "options": question.options,
            "correct_answer": question.correct_answer,
            "explanation": question.explanation
        }
        
        # Regenerate using AI
        new_question_data = AIService.regenerate_question(original_question_data, new_params)
        
        # Update question with new data
        question.question = new_question_data["question"]
        question.type = new_question_data["type"]
        question.difficulty = new_question_data["difficulty"]
        question.style = new_question_data["style"]
        question.options = new_question_data.get("options")
        question.correct_answer = new_question_data["correct_answer"]
        question.explanation = new_question_data.get("explanation")
        question.is_validated = False
        question.is_approved = False
        
        db.commit()
        db.refresh(question)
        
        return question
    
    @staticmethod
    def add_to_question_bank(question_id: int, user_id: int, db: Session) -> QuestionBank:
        """Add a question to user's question bank."""
        # Check if question exists
        question = QuestionService.get_question(question_id, db)
        
        # Check if already in question bank
        existing = db.query(QuestionBank).filter(
            QuestionBank.user_id == user_id,
            QuestionBank.question_id == question_id
        ).first()
        
        if existing:
            return existing
        
        # Add to question bank
        bank_entry = QuestionBank(
            user_id=user_id,
            question_id=question_id
        )
        
        db.add(bank_entry)
        db.commit()
        db.refresh(bank_entry)
        
        return bank_entry
    
    @staticmethod
    def get_question_bank(
        user_id: int,
        db: Session,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        question_type: Optional[str] = None,
        style: Optional[str] = None
    ) -> List[QuestionBank]:
        """Get user's question bank with optional filters."""
        query = db.query(QuestionBank).filter(QuestionBank.user_id == user_id)
        
        # Join with questions to apply filters
        query = query.join(Question)
        
        if topic:
            query = query.filter(Question.topic.ilike(f"%{topic}%"))
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        if question_type:
            query = query.filter(Question.type == question_type)
        if style:
            query = query.filter(Question.style == style)
        
        return query.all()
    
    @staticmethod
    def remove_from_question_bank(bank_id: int, user_id: int, db: Session) -> bool:
        """Remove a question from user's question bank."""
        bank_entry = db.query(QuestionBank).filter(
            QuestionBank.id == bank_id,
            QuestionBank.user_id == user_id
        ).first()
        
        if not bank_entry:
            raise ValueError("Question bank entry not found")
        
        db.delete(bank_entry)
        db.commit()
        
        return True
    
    @staticmethod
    def approve_question(question_id: int, db: Session) -> Question:
        """Approve a question for use in quizzes."""
        question = QuestionService.get_question(question_id, db)
        question.is_approved = True
        db.commit()
        db.refresh(question)
        return question

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import random
import string
from decimal import Decimal

from app.models.quiz import Quiz, QuizQuestion, QuizAttempt, StudentAnswer, Result
from app.models.question import Question
from app.schemas.quiz import QuizCreate, QuizUpdate, QuizAttemptCreate, QuizAttemptSubmit


class QuizService:
    """Service for quiz-related operations."""
    
    @staticmethod
    def generate_quiz_code(db: Optional[Session] = None) -> str:
        """Generate a unique 6-character quiz code."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if db:
                existing = db.query(Quiz).filter(Quiz.quiz_code == code).first()
                if existing:
                    continue
            return code
    
    @staticmethod
    def create_quiz(quiz_data: QuizCreate, professor_id: int, db: Session) -> Quiz:
        """Create a new quiz."""
        # Validate questions exist in database
        questions = db.query(Question).filter(
            Question.id.in_(quiz_data.question_ids)
        ).all()
        
        if len(questions) != len(quiz_data.question_ids):
            # Fetch missing question IDs for clear error reporting or auto-fix
            existing_ids = {q.id for q in questions}
            missing = set(quiz_data.question_ids) - existing_ids
            raise ValueError(f"Questions with IDs {list(missing)} do not exist in database")

        # Auto-approve and auto-validate all questions for the quiz
        for q in questions:
            q.is_approved = True
            q.is_validated = True
        db.commit()
        
        # Create quiz
        quiz_code = QuizService.generate_quiz_code(db)
        new_quiz = Quiz(
            professor_id=professor_id,
            title=quiz_data.title,
            description=quiz_data.description,
            topic=quiz_data.topic,
            time_limit=quiz_data.time_limit,
            start_time=quiz_data.start_time,
            end_time=quiz_data.end_time,
            randomize_questions=quiz_data.randomize_questions,
            randomize_options=quiz_data.randomize_options,
            max_attempts=quiz_data.max_attempts,
            show_immediate_results=quiz_data.show_immediate_results,
            show_correct_answers=quiz_data.show_correct_answers,
            show_explanations=quiz_data.show_explanations,
            passing_percentage=quiz_data.passing_percentage,
            quiz_code=quiz_code,
            is_active=True
        )
        
        db.add(new_quiz)
        db.commit()
        db.refresh(new_quiz)
        
        # Add questions to quiz
        for order, question_id in enumerate(quiz_data.question_ids, 1):
            quiz_question = QuizQuestion(
                quiz_id=new_quiz.id,
                question_id=question_id,
                question_order=order,
                marks=1  # Default marks, can be customized
            )
            db.add(quiz_question)
        
        db.commit()
        
        return new_quiz
    
    @staticmethod
    def get_quiz(quiz_id: int, db: Session) -> Quiz:
        """Get a quiz by ID."""
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise ValueError("Quiz not found")
        return quiz
    
    @staticmethod
    def get_quiz_by_code(quiz_code: str, db: Session) -> Quiz:
        """Get a quiz by code."""
        quiz = db.query(Quiz).filter(Quiz.quiz_code == quiz_code).first()
        if not quiz:
            raise ValueError("Quiz not found")
        return quiz
    
    @staticmethod
    def get_professor_quizzes(professor_id: int, db: Session) -> List[Quiz]:
        """Get all quizzes for a professor."""
        return db.query(Quiz).filter(Quiz.professor_id == professor_id).all()
    
    @staticmethod
    def update_quiz(quiz_id: int, quiz_update: QuizUpdate, db: Session) -> Quiz:
        """Update a quiz."""
        quiz = QuizService.get_quiz(quiz_id, db)
        
        update_data = quiz_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(quiz, field, value)
        
        db.commit()
        db.refresh(quiz)
        
        return quiz
    
    @staticmethod
    def delete_quiz(quiz_id: int, db: Session) -> bool:
        """Delete a quiz."""
        quiz = QuizService.get_quiz(quiz_id, db)
        db.delete(quiz)
        db.commit()
        return True
    
    @staticmethod
    def publish_quiz(quiz_id: int, db: Session) -> Quiz:
        """Publish a quiz (make it active)."""
        quiz = QuizService.get_quiz(quiz_id, db)
        quiz.is_active = True
        db.commit()
        db.refresh(quiz)
        return quiz
    
    @staticmethod
    def start_quiz_attempt(quiz_id: int, student_id: int, db: Session) -> QuizAttempt:
        """Start a quiz attempt for a student."""
        quiz = QuizService.get_quiz(quiz_id, db)
        
        # Check if quiz is active
        if not quiz.is_active:
            raise ValueError("Quiz is not active")
        
        # Check if quiz is within time window
        if quiz.start_time and datetime.utcnow() < quiz.start_time:
            raise ValueError("Quiz has not started yet")
        
        if quiz.end_time and datetime.utcnow() > quiz.end_time:
            raise ValueError("Quiz has ended")
        
        # Check attempt limit
        previous_attempts = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.student_id == student_id
        ).count()
        
        if previous_attempts >= quiz.max_attempts:
            raise ValueError("Maximum attempts reached")
        
        # Create attempt
        attempt_number = previous_attempts + 1
        new_attempt = QuizAttempt(
            quiz_id=quiz_id,
            student_id=student_id,
            status="in_progress",
            attempt_number=attempt_number
        )
        
        db.add(new_attempt)
        db.commit()
        db.refresh(new_attempt)
        
        return new_attempt
    
    @staticmethod
    def submit_quiz_attempt(attempt_id: int, submission_data: QuizAttemptSubmit, db: Session) -> Result:
        """Submit quiz attempt and calculate results."""
        attempt = db.query(QuizAttempt).filter(QuizAttempt.id == attempt_id).first()
        if not attempt:
            raise ValueError("Attempt not found")
        
        if attempt.status != "in_progress":
            raise ValueError("Attempt already submitted")
        
        # Get quiz questions
        quiz_questions = db.query(QuizQuestion).filter(
            QuizQuestion.quiz_id == attempt.quiz_id
        ).all()
        
        total_questions = len(quiz_questions)
        correct_answers = 0
        wrong_answers = 0
        unanswered = 0
        total_marks = sum(qq.marks for qq in quiz_questions)
        obtained_marks = 0
        
        # Process each answer
        answers_dict = {ans["question_id"]: ans for ans in submission_data.answers}
        
        for quiz_question in quiz_questions:
            question = quiz_question.question
            student_answer = answers_dict.get(quiz_question.question_id)
            
            if not student_answer or not student_answer.get("answer"):
                unanswered += 1
                continue
            
            # Check if answer is correct
            is_correct = str(student_answer["answer"]).strip().lower() == str(question.correct_answer).strip().lower()
            
            # Create student answer record
            student_answer_record = StudentAnswer(
                attempt_id=attempt_id,
                question_id=quiz_question.question_id,
                answer=student_answer["answer"],
                is_correct=is_correct,
                time_spent=student_answer.get("time_spent"),
                answered_at=datetime.utcnow()
            )
            db.add(student_answer_record)
            
            if is_correct:
                correct_answers += 1
                obtained_marks += quiz_question.marks
            else:
                wrong_answers += 1
        
        # Calculate percentage
        percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
        
        # Check if passed
        quiz = QuizService.get_quiz(attempt.quiz_id, db)
        passed = percentage >= quiz.passing_percentage
        
        # Update attempt
        attempt.submitted_at = datetime.utcnow()
        attempt.time_taken = int((attempt.submitted_at - attempt.started_at).total_seconds())
        attempt.score = obtained_marks
        attempt.percentage = percentage
        attempt.status = "submitted"
        
        # Create result
        result = Result(
            attempt_id=attempt_id,
            total_questions=total_questions,
            correct_answers=correct_answers,
            wrong_answers=wrong_answers,
            unanswered=unanswered,
            total_marks=total_marks,
            obtained_marks=obtained_marks,
            percentage=percentage,
            passed=passed
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return result
    
    @staticmethod
    def get_quiz_questions_for_student(quiz_id: int, db: Session) -> List[dict]:
        """Get quiz questions for a student (with randomization if enabled)."""
        quiz = QuizService.get_quiz(quiz_id, db)
        
        quiz_questions = db.query(QuizQuestion).filter(
            QuizQuestion.quiz_id == quiz_id
        ).all()
        
        # Randomize questions if enabled
        if quiz.randomize_questions:
            quiz_questions = random.sample(quiz_questions, len(quiz_questions))
        
        questions_data = []
        for qq in quiz_questions:
            question = qq.question
            options = question.options.copy() if question.options else None
            
            # Randomize options if enabled
            if quiz.randomize_options and options:
                random.shuffle(options)
            
            questions_data.append({
                "id": question.id,
                "question": question.question,
                "type": question.type,
                "options": options,
                "marks": qq.marks,
                "order": qq.question_order
            })
        
        return questions_data
    
    @staticmethod
    def get_quiz_attempts(quiz_id: int, db: Session) -> List[QuizAttempt]:
        """Get all attempts for a quiz."""
        return db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    
    @staticmethod
    def get_student_attempts(student_id: int, db: Session) -> List[QuizAttempt]:
        """Get all attempts for a student."""
        return db.query(QuizAttempt).filter(QuizAttempt.student_id == student_id).all()

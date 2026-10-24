from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from sqlalchemy import func, and_
from decimal import Decimal

from app.models.quiz import Quiz, QuizAttempt, Result, StudentAnswer
from app.models.user import User
from app.models.analytics import PerformanceRecord
from app.schemas.analytics import (
    ProfessorOverview,
    QuizAnalytics,
    StudentPerformance,
    QuizStudentResults,
    StudentOverview,
    StudentPerformanceRecord as StudentPerformanceRecordSchema,
)
from app.services.ai_service import AIService


class AnalyticsService:
    """Service for analytics and reporting operations."""
    
    @staticmethod
    def get_professor_overview(professor_id: int, db: Session) -> ProfessorOverview:
        """Get professor's dashboard overview."""
        # Total quizzes
        total_quizzes = db.query(Quiz).filter(Quiz.professor_id == professor_id).count()
        
        # Active quizzes
        active_quizzes = db.query(Quiz).filter(
            and_(
                Quiz.professor_id == professor_id,
                Quiz.is_active == True
            )
        ).count()
        
        # Completed quizzes (has attempts)
        completed_quizzes = db.query(Quiz).filter(
            and_(
                Quiz.professor_id == professor_id,
                Quiz.id.in_(
                    db.query(QuizAttempt.quiz_id).distinct()
                )
            )
        ).count()
        
        # Total unique students
        total_students = db.query(func.count(func.distinct(QuizAttempt.student_id))).join(Quiz).filter(
            Quiz.professor_id == professor_id
        ).scalar() or 0
        
        # Average score across all attempts
        avg_score_result = db.query(func.avg(Result.percentage)).join(QuizAttempt).join(Quiz).filter(
            Quiz.professor_id == professor_id
        ).first()
        
        average_score = avg_score_result[0] if avg_score_result and avg_score_result[0] else None
        
        # Highest score
        highest_score_result = db.query(func.max(Result.percentage)).join(QuizAttempt).join(Quiz).filter(
            Quiz.professor_id == professor_id
        ).first()
        
        highest_score = highest_score_result[0] if highest_score_result and highest_score_result[0] else None
        
        # Lowest score
        lowest_score_result = db.query(func.min(Result.percentage)).join(QuizAttempt).join(Quiz).filter(
            Quiz.professor_id == professor_id
        ).first()
        
        lowest_score = lowest_score_result[0] if lowest_score_result and lowest_score_result[0] else None
        
        return ProfessorOverview(
            total_quizzes=total_quizzes,
            active_quizzes=active_quizzes,
            completed_quizzes=completed_quizzes,
            total_students=total_students,
            average_score=average_score,
            highest_score=highest_score,
            lowest_score=lowest_score
        )
    
    @staticmethod
    def get_quiz_analytics(quiz_id: int, db: Session) -> QuizAnalytics:
        """Get detailed analytics for a specific quiz."""
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise ValueError("Quiz not found")
        
        # Total attempts
        total_attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).count()
        
        # Average score
        avg_score_result = db.query(func.avg(Result.percentage)).join(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id
        ).first()
        
        average_score = avg_score_result[0] if avg_score_result and avg_score_result[0] else None
        
        # Highest score
        highest_score_result = db.query(func.max(Result.percentage)).join(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id
        ).first()
        
        highest_score = highest_score_result[0] if highest_score_result and highest_score_result[0] else None
        
        # Lowest score
        lowest_score_result = db.query(func.min(Result.percentage)).join(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id
        ).first()
        
        lowest_score = lowest_score_result[0] if lowest_score_result and lowest_score_result[0] else None
        
        # Pass rate
        passed_attempts = db.query(Result).join(QuizAttempt).filter(
            and_(
                QuizAttempt.quiz_id == quiz_id,
                Result.passed == True
            )
        ).count()
        
        pass_rate = (passed_attempts / total_attempts * 100) if total_attempts > 0 else None
        
        # Average time taken
        avg_time_result = db.query(func.avg(QuizAttempt.time_taken)).filter(
            QuizAttempt.quiz_id == quiz_id
        ).first()
        
        average_time = int(avg_time_result[0]) if avg_time_result and avg_time_result[0] else None
        
        # Score distribution
        score_ranges = {
            "0-20": 0,
            "21-40": 0,
            "41-60": 0,
            "61-80": 0,
            "81-100": 0
        }
        
        results = db.query(Result).join(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
        for result in results:
            percentage = float(result.percentage)
            if percentage <= 20:
                score_ranges["0-20"] += 1
            elif percentage <= 40:
                score_ranges["21-40"] += 1
            elif percentage <= 60:
                score_ranges["41-60"] += 1
            elif percentage <= 80:
                score_ranges["61-80"] += 1
            else:
                score_ranges["81-100"] += 1
        
        # Most difficult questions (most incorrect)
        incorrect_counts = db.query(
            StudentAnswer.question_id,
            func.count(StudentAnswer.id).label('incorrect_count')
        ).join(QuizAttempt).filter(
            and_(
                QuizAttempt.quiz_id == quiz_id,
                StudentAnswer.is_correct == False
            )
        ).group_by(StudentAnswer.question_id).order_by(
            func.count(StudentAnswer.id).desc()
        ).limit(5).all()
        
        most_difficult_questions = []
        for question_id, count in incorrect_counts:
            from app.models.question import Question
            question = db.query(Question).filter(Question.id == question_id).first()
            if question:
                most_difficult_questions.append({
                    "question_id": question_id,
                    "question": question.question,
                    "incorrect_count": count
                })
        
        # Topic-wise performance (simplified - based on quiz topic)
        topic_wise_performance = {
            quiz.topic: {
                "average_score": average_score,
                "total_attempts": total_attempts
            }
        } if quiz.topic else {}
        
        return QuizAnalytics(
            quiz_id=quiz_id,
            quiz_title=quiz.title,
            total_attempts=total_attempts,
            average_score=average_score,
            highest_score=highest_score,
            lowest_score=lowest_score,
            pass_rate=pass_rate,
            average_time=average_time,
            score_distribution=score_ranges,
            most_difficult_questions=most_difficult_questions,
            most_incorrect_questions=most_difficult_questions,  # Same for now
            topic_wise_performance=topic_wise_performance
        )
    
    @staticmethod
    def get_quiz_student_results(quiz_id: int, db: Session) -> QuizStudentResults:
        """Get student results for a specific quiz."""
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise ValueError("Quiz not found")
        
        # Get all attempts with results
        attempts = db.query(QuizAttempt, Result, User).join(Result).join(User).filter(
            QuizAttempt.quiz_id == quiz_id
        ).all()
        
        students = []
        for attempt, result, user in attempts:
            students.append(StudentPerformance(
                student_id=user.id,
                student_name=user.full_name,
                score=result.obtained_marks,
                total_marks=result.total_marks,
                percentage=result.percentage
            ))
        
        return QuizStudentResults(
            quiz_id=quiz_id,
            quiz_title=quiz.title,
            students=students
        )
    
    @staticmethod
    def get_student_overview(student_id: int, db: Session) -> StudentOverview:
        """Get student's performance overview."""
        # Total quizzes attempted
        total_quizzes = db.query(QuizAttempt).filter(
            QuizAttempt.student_id == student_id,
            QuizAttempt.status == "submitted"
        ).count()
        
        # Average percentage
        avg_percentage_result = db.query(func.avg(Result.percentage)).join(QuizAttempt).filter(
            QuizAttempt.student_id == student_id
        ).first()
        
        average_percentage = avg_percentage_result[0] if avg_percentage_result and avg_percentage_result[0] else None
        
        # Highest percentage
        highest_percentage_result = db.query(func.max(Result.percentage)).join(QuizAttempt).filter(
            QuizAttempt.student_id == student_id
        ).first()
        
        highest_percentage = highest_percentage_result[0] if highest_percentage_result and highest_percentage_result[0] else None
        
        # Lowest percentage
        lowest_percentage_result = db.query(func.min(Result.percentage)).join(QuizAttempt).filter(
            QuizAttempt.student_id == student_id
        ).first()
        
        lowest_percentage = lowest_percentage_result[0] if lowest_percentage_result and lowest_percentage_result[0] else None
        
        # Total questions answered
        total_questions = db.query(func.sum(Result.total_questions)).join(QuizAttempt).filter(
            QuizAttempt.student_id == student_id
        ).first()
        
        total_questions_answered = int(total_questions[0]) if total_questions and total_questions[0] else 0
        
        # Correct answers
        correct_answers = db.query(func.sum(Result.correct_answers)).join(QuizAttempt).filter(
            QuizAttempt.student_id == student_id
        ).first()
        
        total_correct = int(correct_answers[0]) if correct_answers and correct_answers[0] else 0
        
        # Accuracy
        accuracy = (total_correct / total_questions_answered * 100) if total_questions_answered > 0 else None
        
        # Get performance records for strong/weak topics
        performance_records = db.query(PerformanceRecord).filter(
            PerformanceRecord.student_id == student_id
        ).all()
        
        strong_topics = []
        weak_topics = []
        
        for record in performance_records:
            if record.strength:
                import json
                strong_topics.extend(json.loads(record.strength))
            if record.weakness:
                import json
                weak_topics.extend(json.loads(record.weakness))
        
        return StudentOverview(
            total_quizzes_attempted=total_quizzes,
            average_percentage=average_percentage,
            highest_percentage=highest_percentage,
            lowest_percentage=lowest_percentage,
            strong_topics=list(set(strong_topics)),
            weak_topics=list(set(weak_topics)),
            total_questions_answered=total_questions_answered,
            correct_answers=total_correct,
            accuracy=accuracy
        )
    
    @staticmethod
    def update_student_performance(student_id: int, topic: str, score: Decimal, db: Session):
        """Update student performance record for a topic."""
        # Get or create performance record
        record = db.query(PerformanceRecord).filter(
            and_(
                PerformanceRecord.student_id == student_id,
                PerformanceRecord.topic == topic
            )
        ).first()
        
        if not record:
            record = PerformanceRecord(
                student_id=student_id,
                topic=topic,
                total_quizzes=0,
                total_questions=0,
                correct_answers=0
            )
            db.add(record)
        
        # Update record
        record.total_quizzes += 1
        # Assuming 10 questions per quiz for simplicity
        record.total_questions += 10
        # Assuming score is percentage, convert to correct answers
        record.correct_answers += int(score * 10 / 100)
        record.average_score = (record.correct_answers / record.total_questions * 100) if record.total_questions > 0 else 0
        
        # Determine strength/weakness
        if record.average_score >= 70:
            import json
            if not record.strength:
                record.strength = json.dumps([topic])
            else:
                strengths = json.loads(record.strength)
                if topic not in strengths:
                    strengths.append(topic)
                record.strength = json.dumps(strengths)
        elif record.average_score < 50:
            import json
            if not record.weakness:
                record.weakness = json.dumps([topic])
            else:
                weaknesses = json.loads(record.weakness)
                if topic not in weaknesses:
                    weaknesses.append(topic)
                record.weakness = json.dumps(weaknesses)
        
        db.commit()
    
    @staticmethod
    def get_student_performance_records(student_id: int, db: Session) -> List[StudentPerformanceRecordSchema]:
        """Get student's performance records by topic."""
        records = db.query(PerformanceRecord).filter(
            PerformanceRecord.student_id == student_id
        ).all()
        
        performance_records = []
        for record in records:
            import json
            strength_list = json.loads(record.strength) if record.strength else []
            weakness_list = json.loads(record.weakness) if record.weakness else []
            
            performance_records.append(StudentPerformanceRecordSchema(
                topic=record.topic,
                total_quizzes=record.total_quizzes,
                total_questions=record.total_questions,
                correct_answers=record.correct_answers,
                average_score=record.average_score,
                strength=strength_list,
                weakness=weakness_list,
                last_updated=record.last_updated
            ))
        
        return performance_records
    
    @staticmethod
    def get_student_performance_trends(student_id: int, db: Session) -> List[dict]:
        """Get student's performance trends over time."""
        results = db.query(Result, Quiz, QuizAttempt).join(QuizAttempt).join(Quiz).filter(
            QuizAttempt.student_id == student_id,
            QuizAttempt.status == "submitted"
        ).order_by(QuizAttempt.submitted_at.desc()).all()
        
        trends = []
        for result, quiz, attempt in results:
            trends.append({
                "quiz_title": quiz.title,
                "date": attempt.submitted_at,
                "percentage": result.percentage,
                "time_taken": attempt.time_taken
            })
        
        return trends
    
    @staticmethod
    def generate_ai_feedback(student_id: int, db: Session) -> dict:
        """Generate AI feedback for student performance."""
        overview = AnalyticsService.get_student_overview(student_id, db)
        performance_records = AnalyticsService.get_student_performance_records(student_id, db)
        
        performance_data = {
            "overview": {
                "total_quizzes": overview.total_quizzes_attempted,
                "average_percentage": str(overview.average_percentage) if overview.average_percentage else 0,
                "strong_topics": overview.strong_topics,
                "weak_topics": overview.weak_topics,
                "accuracy": str(overview.accuracy) if overview.accuracy else 0
            },
            "topic_performance": [
                {
                    "topic": record.topic,
                    "average_score": str(record.average_score) if record.average_score else 0,
                    "total_quizzes": record.total_quizzes
                }
                for record in performance_records
            ]
        }
        
        # Get student name
        student = db.query(User).filter(User.id == student_id).first()
        student_name = student.full_name if student else "Student"
        
        try:
            feedback = AIService.generate_performance_feedback(student_name, performance_data)
            return feedback
        except Exception as e:
            # Fallback to basic feedback if AI fails
            return {
                "feedback": f"You have attempted {overview.total_quizzes_attempted} quizzes with an average score of {overview.average_percentage}%.",
                "strong_areas": overview.strong_topics,
                "weak_areas": overview.weak_topics,
                "recommendations": ["Focus more practice on weak areas", "Review explanations for incorrect answers"]
            }

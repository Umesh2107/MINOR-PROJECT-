from sqlalchemy.orm import Session
from app.models.user import User, Role
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password


class AuthService:
    """Service for authentication-related operations."""
    
    @staticmethod
    def create_user(user_data: UserCreate, db: Session) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Check if role exists
        role = db.query(Role).filter(Role.id == user_data.role_id).first()
        if not role:
            raise ValueError("Invalid role")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            role_id=user_data.role_id,
            full_name=user_data.full_name
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def authenticate_user(email: str, password: str, db: Session) -> User:
        """Authenticate user with email and password."""
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise ValueError("Incorrect email or password")
        
        if not verify_password(password, user.password_hash):
            raise ValueError("Incorrect email or password")
        
        if not user.is_active:
            raise ValueError("Inactive user")
        
        return user
    
    @staticmethod
    def get_user_by_email(email: str, db: Session) -> User:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(user_id: int, db: Session) -> User:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

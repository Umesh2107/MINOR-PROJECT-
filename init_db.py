"""
Database initialization script for Smart Quiz Assistant.
Creates database tables, roles, and default pre-seeded demo accounts.
"""
from app.core.database import engine, Base, SessionLocal
from app.models.user import Role, User
from app.core.security import get_password_hash

def init_database():
    """Initialize database with tables and default demo data."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Create default roles if missing
        prof_role = db.query(Role).filter(Role.name == "professor").first()
        if not prof_role:
            prof_role = Role(
                id=1,
                name="professor",
                description="Can create quizzes, generate questions, view analytics"
            )
            db.add(prof_role)
            
        stud_role = db.query(Role).filter(Role.name == "student").first()
        if not stud_role:
            stud_role = Role(
                id=2,
                name="student",
                description="Can take quizzes, view own results"
            )
            db.add(stud_role)

        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(
                id=3,
                name="admin",
                description="System Administrator with full monitoring and user management privileges"
            )
            db.add(admin_role)
        
        db.commit()

        # 2. Pre-seed default accounts
        default_accounts = [
            {"email": "admin@example.com", "full_name": "System Administrator", "role_id": 3},
            {"email": "admin_test@example.com", "full_name": "Admin Test Account", "role_id": 3},
            {"email": "prof_test@example.com", "full_name": "Professor Test", "role_id": 1},
            {"email": "student_test@example.com", "full_name": "Student Test", "role_id": 2},
            {"email": "professor@example.com", "full_name": "Demo Professor", "role_id": 1},
            {"email": "student@example.com", "full_name": "Demo Student", "role_id": 2},
        ]

        for acc in default_accounts:
            existing_user = db.query(User).filter(User.email == acc["email"]).first()
            if not existing_user:
                new_user = User(
                    email=acc["email"],
                    full_name=acc["full_name"],
                    role_id=acc["role_id"],
                    password_hash=get_password_hash("Password123!"),
                    is_active=True
                )
                db.add(new_user)
        
        db.commit()
        print("Database roles and demo user accounts initialized successfully!")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()

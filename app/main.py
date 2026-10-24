from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.endpoints import auth, users, topics, materials, questions, quizzes, attempts, analytics

from init_db import init_database

# Create database tables and seed default roles/users
init_database()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Smart Quiz & Learning Assistant API"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.endpoints import auth, users, topics, materials, questions, quizzes, attempts, analytics, admin

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(topics.router, prefix="/api/topics", tags=["Topics"])
app.include_router(materials.router, prefix="/api/materials", tags=["Materials"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(quizzes.router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(attempts.router, prefix="/api/attempts", tags=["Quiz Attempts"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Monitoring"])


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Smart Quiz Assistant API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/api/network-ip")
def get_network_ip():
    import socket
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass
    return {
        "ip": local_ip,
        "vite_port": 5173
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

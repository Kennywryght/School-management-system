from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, admin, teachers, students

# Create FastAPI app
app = FastAPI(
    title="School Management System API",
    description="API for managing students, teachers, and results",
    version="1.0.0"
)

# Configure CORS (so frontend can connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(teachers.router)
app.include_router(students.router)

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Welcome to School Management System API",
        "status": "running",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Test database connection endpoint
@app.get("/test-db")
def test_database():
    from app.database import engine
    try:
        with engine.connect() as connection:
            return {
                "status": "success",
                "message": "Database connection successful"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }  
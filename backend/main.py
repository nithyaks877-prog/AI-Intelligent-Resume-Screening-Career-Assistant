from fastapi import FastAPI

from backend.routers.student import router as student_router
from backend.routers.recruiter import router as recruiter_router
from backend.routers.auth import router as auth_router

app = FastAPI(
    title="HireSense AI API",
    version="1.0.0",
    description="Backend API for HireSense AI"
)

app.include_router(student_router)
app.include_router(recruiter_router)
app.include_router(auth_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to HireSense AI Backend"
    }
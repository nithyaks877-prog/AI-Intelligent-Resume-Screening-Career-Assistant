from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from ml.parser import extract_text
from ml.skill_extractor import extract_skills
from ml.similarity import compare_skills
from ml.ats_score import calculate_ats_score
from ml.gemini_service import (
    generate_feedback,
    optimize_resume,
    generate_interview_questions,
    generate_learning_plan
)

from backend.database.database import get_db
from backend.database.models import User, Resume, Report
from backend.utils.dependencies import get_current_user

router = APIRouter(
    prefix="/student",
    tags=["Student"]
)


@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Resume Text
    resume_text = extract_text(resume)

    # Resume Skills
    resume_skills = extract_skills(resume_text)

    # JD Skills
    jd_skills = extract_skills(job_description)

    # Skill Comparison
    comparison = compare_skills(
        resume_skills,
        jd_skills
    )

    # ATS Score
    ats_score, breakdown = calculate_ats_score(
        comparison,
        resume_text,
        job_description
    )

    # AI Feedback
    feedback = generate_feedback(
        resume_text,
        job_description,
        ats_score,
        comparison["matched"],
        comparison["missing"]
    )

    # Resume Optimization
    optimized_resume = optimize_resume(
        resume_text,
        job_description
    )

    # AI Interview Questions
    interview_questions = generate_interview_questions(
        job_description,
        comparison["missing"]
    )

    # Personalized Learning Plan
    learning_plan = generate_learning_plan(
        comparison["missing"]
    )

    # -----------------------------
    # Save to Database
    # -----------------------------
    new_resume = Resume(
        user_id=current_user.id,
        resume_path=resume.filename,
        ats_score=ats_score
    )
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    new_report = Report(
        resume_id=new_resume.id,
        feedback=feedback,
        recommendation=None
    )
    db.add(new_report)
    db.commit()

    return {
        "resume_id": new_resume.id,

        "resume_text": resume_text,
        "job_description": job_description,

        "resume_skills": resume_skills,
        "jd_skills": jd_skills,

        "matched_skills": comparison["matched"],
        "missing_skills": comparison["missing"],
        "extra_skills": comparison["extra"],

        "match_percentage": comparison["match_percentage"],

        "ats_score": ats_score,
        "breakdown": breakdown,

        "feedback": feedback,
        "optimized_resume": optimized_resume,

        "interview_questions": interview_questions,
        "learning_plan": learning_plan
    }


@router.get("/history")
def get_resume_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all past resume analyses for the logged-in user,
    most recent first.
    """
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )

    return [
        {
            "resume_id": r.id,
            "resume_path": r.resume_path,
            "ats_score": r.ats_score,
            "created_at": r.created_at
        }
        for r in resumes
    ]


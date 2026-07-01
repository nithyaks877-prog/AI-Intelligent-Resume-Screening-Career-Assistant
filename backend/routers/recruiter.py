from fastapi import APIRouter, UploadFile, File, Form, Depends
from typing import List

from ml.parser import extract_text
from ml.skill_extractor import extract_skills
from ml.similarity import compare_skills
from ml.ats_score import calculate_ats_score
from ml.gemini_service import candidate_summary
from ml.recommendation import hiring_recommendation

from backend.database.models import User
from backend.utils.dependencies import get_current_user

router = APIRouter(
    prefix="/recruiter",
    tags=["Recruiter"]
)


@router.get("/")
def recruiter_home():
    return {
        "message": "Recruiter API Working"
    }


@router.post("/analyze")
async def analyze_candidates(
    resumes: List[UploadFile] = File(...),
    job_description: str = Form(...),
    current_user: User = Depends(get_current_user)
):

    # -----------------------------
    # Job Description
    # -----------------------------
    jd_text = job_description
    jd_skills = extract_skills(jd_text)

    # -----------------------------
    # Analyze Every Resume
    # -----------------------------
    results = []

    for resume in resumes:

        resume_text = extract_text(resume)
        resume_skills = extract_skills(resume_text)

        comparison = compare_skills(
            resume_skills,
            jd_skills
        )

        ats_score, breakdown = calculate_ats_score(
            comparison,
            resume_text,
            jd_text
        )

        recommendation = hiring_recommendation(ats_score)

        summary = candidate_summary(
            resume_text,
            jd_text,
            ats_score,
            comparison["matched"],
            comparison["missing"]
        )

        results.append({
            "candidate": resume.filename,
            "ats_score": ats_score,
            "skill_match": comparison["match_percentage"],
            "recommendation": recommendation,
            "matched_skills": comparison["matched"],
            "missing_skills": comparison["missing"],
            "ai_summary": summary
        })

    # -----------------------------
    # Sort Candidates (highest ATS score first)
    # -----------------------------
    results.sort(
        key=lambda x: x["ats_score"],
        reverse=True
    )

    # -----------------------------
    # Dashboard Metrics
    # -----------------------------
    total_candidates = len(results)

    average_ats = round(
        sum(r["ats_score"] for r in results) / total_candidates,
        2
    )

    best_candidate = results[0]["candidate"]

    recommended_count = sum(
        1
        for r in results
        if r["recommendation"] in [
            "🟢 Strongly Recommend",
            "🟡 Recommend"
        ]
    )

    return {
        "results": results,
        "total_candidates": total_candidates,
        "average_ats": average_ats,
        "best_candidate": best_candidate,
        "recommended_count": recommended_count
    }


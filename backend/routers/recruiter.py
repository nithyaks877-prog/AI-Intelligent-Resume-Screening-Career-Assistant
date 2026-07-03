from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List

from ml.parser import extract_text
from ml.skill_extractor import extract_skills
from ml.similarity import compare_skills
from ml.ats_score import calculate_ats_score
from ml.gemini_service import candidate_summary
from ml.recommendation import hiring_recommendation

from backend.database.database import get_db
from backend.database.models import User, JobDescription, Candidate
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
    role_title: str = Form("Untitled Role"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------
    # Job Description
    # -----------------------------
    jd_text = job_description
    jd_skills = extract_skills(jd_text)

    # -----------------------------
    # Save Job Description
    # -----------------------------
    new_job = JobDescription(
        recruiter_id=current_user.id,
        title=role_title,
        skills=", ".join(jd_skills),
        raw_text=jd_text
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

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

        # -----------------------------
        # Save Candidate
        # -----------------------------
        new_candidate = Candidate(
            job_description_id=new_job.id,
            candidate_name=resume.filename,
            ats_score=float(ats_score),
            skill_match=float(comparison["match_percentage"]),
            matched_skills=", ".join(comparison["matched"]),
            missing_skills=", ".join(comparison["missing"]),
            ai_summary=summary,
            recommendation=recommendation,
            status="Applied"
        )
        db.add(new_candidate)
        db.commit()
        db.refresh(new_candidate)

        results.append({
            "candidate_id": new_candidate.id,
            "candidate": resume.filename,
            "ats_score": ats_score,
            "skill_match": comparison["match_percentage"],
            "recommendation": recommendation,
            "matched_skills": comparison["matched"],
            "missing_skills": comparison["missing"],
            "ai_summary": summary,
            "status": "Applied"
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
        "job_description_id": new_job.id,
        "results": results,
        "total_candidates": total_candidates,
        "average_ats": average_ats,
        "best_candidate": best_candidate,
        "recommended_count": recommended_count
    }


@router.patch("/candidates/{candidate_id}/status")
def update_candidate_status(
    candidate_id: int,
    status: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a candidate's pipeline status
    (Applied, Screening, Interview, Assessment, Hired).
    """
    candidate = (
        db.query(Candidate)
        .join(JobDescription)
        .filter(
            Candidate.id == candidate_id,
            JobDescription.recruiter_id == current_user.id
        )
        .first()
    )

    if not candidate:
        return {"error": "Candidate not found or not owned by you."}

    candidate.status = status
    db.commit()

    return {"candidate_id": candidate.id, "status": candidate.status}


@router.get("/pipeline")
def get_pipeline_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns candidate counts grouped by pipeline status,
    across all job postings this recruiter has created.
    """
    candidates = (
        db.query(Candidate)
        .join(JobDescription)
        .filter(JobDescription.recruiter_id == current_user.id)
        .all()
    )

    statuses = ["Applied", "Screening", "Interview", "Assessment", "Hired"]
    counts = {status: 0 for status in statuses}

    for c in candidates:
        if c.status in counts:
            counts[c.status] += 1

    return {
        "total_candidates": len(candidates),
        "counts": counts
    }


@router.get("/analytics")
def get_weekly_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns real, derived analytics for the last 7 days:
    - Daily application counts (for a trend chart)
    - Daily average ATS score
    - Overall shortlist rate (% of candidates moved past "Applied")

    All values are computed from actual saved candidate data —
    no fabricated metrics.
    """

    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    candidates = (
        db.query(Candidate)
        .join(JobDescription)
        .filter(
            JobDescription.recruiter_id == current_user.id,
            Candidate.created_at >= seven_days_ago
        )
        .all()
    )

    # -----------------------------
    # Group by day
    # -----------------------------
    daily_data = {}

    for c in candidates:
        day_key = c.created_at.strftime("%Y-%m-%d")

        if day_key not in daily_data:
            daily_data[day_key] = {"applications": 0, "total_ats": 0}

        daily_data[day_key]["applications"] += 1
        daily_data[day_key]["total_ats"] += c.ats_score or 0

    daily = [
        {
            "date": day,
            "applications": data["applications"],
            "avg_ats": round(data["total_ats"] / data["applications"], 2)
        }
        for day, data in sorted(daily_data.items())
    ]

    # -----------------------------
    # Shortlist rate (moved past "Applied")
    # -----------------------------
    total = len(candidates)
    shortlisted = sum(1 for c in candidates if c.status != "Applied")

    shortlist_rate = round((shortlisted / total) * 100, 2) if total > 0 else 0

    # -----------------------------
    # Week peak (busiest day)
    # -----------------------------
    week_peak = max(
        (d["applications"] for d in daily),
        default=0
    )

    return {
        "daily": daily,
        "shortlist_rate": shortlist_rate,
        "week_peak": week_peak,
        "total_this_week": total
    }

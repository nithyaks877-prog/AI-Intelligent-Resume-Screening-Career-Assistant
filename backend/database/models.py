from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="student")  # student or recruiter
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resumes = relationship("Resume", back_populates="owner")
    job_descriptions = relationship("JobDescription", back_populates="recruiter")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resume_path = Column(String, nullable=True)
    ats_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="resumes")
    reports = relationship("Report", back_populates="resume")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=True)
    skills = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    recruiter = relationship("User", back_populates="job_descriptions")
    candidates = relationship("Candidate", back_populates="job_description")


class Candidate(Base):
    """
    Represents one resume analyzed by a recruiter against a
    specific job posting. Tracks hiring pipeline status.
    """
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"))

    candidate_name = Column(String, nullable=True)  # from resume filename
    ats_score = Column(Float, nullable=True)
    skill_match = Column(Float, nullable=True)
    matched_skills = Column(Text, nullable=True)   # stored as comma-separated
    missing_skills = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    recommendation = Column(String, nullable=True)

    # Pipeline status: Applied -> Screening -> Interview -> Assessment -> Hired
    status = Column(String, default="Applied")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    job_description = relationship("JobDescription", back_populates="candidates")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    feedback = Column(Text, nullable=True)
    recommendation = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="reports")

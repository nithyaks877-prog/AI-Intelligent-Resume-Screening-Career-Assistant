import sys
from pathlib import Path

# ---------------------------
# Add project root to Python path
# ---------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# ---------------------------
# Imports
# ---------------------------
import streamlit as st
import requests

from ml.parser import extract_text
from ml.pdf_report import create_pdf_report
from frontend.auth import require_login, get_auth_headers

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="HireSense AI",
    page_icon="📄",
    layout="centered"
)

# ---------------------------
# Require Login
# ---------------------------
require_login()

# ---------------------------
# Header
# ---------------------------
st.title("📄 HireSense AI")
st.subheader("AI Resume Screening & Career Assistant")

st.markdown("---")

st.header("👤 Student Dashboard")

# ---------------------------
# Resume Upload
# ---------------------------
resume_file = st.file_uploader(
    "📄 Upload Resume",
    type=["pdf", "docx"]
)

# ---------------------------
# Job Description Upload
# ---------------------------
jd_file = st.file_uploader(
    "📋 Upload Job Description (Optional)",
    type=["pdf", "docx", "txt"]
)

st.markdown("### OR")

jd_text = st.text_area(
    "✍️ Paste Job Description",
    height=200,
    placeholder="Paste the job description here..."
)

st.markdown("---")

# ---------------------------
# Analyze Button
# ---------------------------
if st.button("🚀 Analyze Resume", use_container_width=True):

    if resume_file is None:
        st.error("Please upload your resume.")

    elif jd_file is None and jd_text.strip() == "":
        st.error("Please upload or paste a Job Description.")

    else:

        # -----------------------------
        # Read Job Description
        # -----------------------------
        if jd_file:
            jd_text_content = extract_text(jd_file)
        else:
            jd_text_content = jd_text

        # -----------------------------
        # Call FastAPI Backend (with auth token)
        # -----------------------------
        response = requests.post(
            "http://127.0.0.1:8000/student/analyze",
            headers=get_auth_headers(),
            files={
                "resume": (
                    resume_file.name,
                    resume_file,
                    resume_file.type
                )
            },
            data={
                "job_description": jd_text_content
            }
        )

        if response.status_code == 401:
            st.error("Your session expired. Please log in again.")
            from frontend.auth import logout
            logout()
            st.rerun()

        elif response.status_code != 200:
            st.error("Backend Error")
            st.write(response.text)
            st.stop()

        else:
            result = response.json()

            # -----------------------------
            # Unpack Response
            # -----------------------------
            resume_text = result["resume_text"]
            resume_skills = result["resume_skills"]
            jd_skills = result["jd_skills"]

            matched = result["matched_skills"]
            missing = result["missing_skills"]
            extra = result["extra_skills"]

            match_percentage = result["match_percentage"]
            ats_score = result["ats_score"]
            breakdown = result["breakdown"]

            feedback = result["feedback"]
            optimized_resume = result["optimized_resume"]

            # -----------------------------
            # ATS Score
            # -----------------------------
            st.header("🎯 ATS Score")

            st.metric(
                "Overall ATS Score",
                f"{ats_score}/100"
            )

            st.subheader("📊 Score Breakdown")
            st.write(breakdown)

            # -----------------------------
            # AI Feedback
            # -----------------------------
            st.header("🤖 AI Resume Feedback")
            st.write(feedback)

            # -----------------------------
            # Skill Comparison
            # -----------------------------
            st.subheader("✅ Matched Skills")
            st.write(matched)

            st.subheader("❌ Missing Skills")
            st.write(missing)

            st.subheader("⭐ Extra Skills")
            st.write(extra)

            st.metric(
                label="📊 Skill Match Percentage",
                value=f"{match_percentage}%"
            )

            # -----------------------------
            # Optimized Resume
            # -----------------------------
            st.markdown("---")
            st.header("✨ ATS Optimized Resume")

            st.text_area(
                "Optimized Resume",
                optimized_resume,
                height=500
            )

            # -----------------------------
            # PDF Report Download
            # -----------------------------
            create_pdf_report(
                "ATS_Report.pdf",
                ats_score,
                resume_skills,
                jd_skills,
                matched,
                missing,
                feedback
            )

            with open("ATS_Report.pdf", "rb") as pdf_file:
                st.download_button(
                    label="📥 Download ATS Report",
                    data=pdf_file,
                    file_name="ATS_Report.pdf",
                    mime="application/pdf"
                )

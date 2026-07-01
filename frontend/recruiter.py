import sys
from pathlib import Path

# -----------------------------
# Add Project Root
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# -----------------------------
# Imports
# -----------------------------
import streamlit as st
import pandas as pd
import requests

from ml.parser import extract_text
from ml.recruiter_report import create_recruiter_report
from frontend.auth import require_login, get_auth_headers

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="HireSense AI - Recruiter",
    page_icon="👨‍💼",
    layout="wide"
)

# -----------------------------
# Require Login
# -----------------------------
require_login()

# -----------------------------
# Header
# -----------------------------
st.title("👨‍💼 HireSense AI")
st.subheader("Recruiter Dashboard")

st.markdown("---")

# -----------------------------
# Upload Job Description
# -----------------------------
jd_file = st.file_uploader(
    "📋 Upload Job Description",
    type=["pdf", "docx", "txt"]
)

# -----------------------------
# Upload Multiple Resumes
# -----------------------------
resume_files = st.file_uploader(
    "📄 Upload Candidate Resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

st.markdown("---")

# -----------------------------
# Analyze Button
# -----------------------------
analyze = st.button(
    "🚀 Analyze Candidates",
    use_container_width=True
)

# -----------------------------
# Analyze Candidates
# -----------------------------
if analyze:

    if jd_file is None:
        st.error("Please upload a Job Description.")

    elif not resume_files:
        st.error("Please upload candidate resumes.")

    else:

        # -----------------------------
        # Extract Job Description Text
        # -----------------------------
        jd_text = extract_text(jd_file)

        st.success(f"Analyzing {len(resume_files)} candidates...")

        # -----------------------------
        # Call FastAPI Backend (with auth token)
        # -----------------------------
        files_payload = [
            (
                "resumes",
                (resume.name, resume, resume.type)
            )
            for resume in resume_files
        ]

        response = requests.post(
            "http://127.0.0.1:8000/recruiter/analyze",
            headers=get_auth_headers(),
            files=files_payload,
            data={"job_description": jd_text}
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
            data = response.json()

            results = data["results"]
            total_candidates = data["total_candidates"]
            average_ats = data["average_ats"]
            best_candidate = data["best_candidate"]
            recommended_count = data["recommended_count"]

            # -----------------------------
            # Build PDF Report
            # -----------------------------
            report_rows = [
                {
                    "Candidate": r["candidate"],
                    "ATS Score": r["ats_score"],
                    "Skill Match": r["skill_match"],
                    "Recommendation": r["recommendation"],
                    "Matched": r["matched_skills"],
                    "Missing": r["missing_skills"],
                    "AI Summary": r["ai_summary"]
                }
                for r in results
            ]

            create_recruiter_report(
                "Recruiter_Report.pdf",
                report_rows
            )

            # -----------------------------
            # Dashboard Overview
            # -----------------------------
            st.subheader("📈 Dashboard Overview")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("👥 Candidates", total_candidates)

            with col2:
                st.metric("📊 Average ATS", average_ats)

            with col3:
                st.metric("🏆 Best Candidate", best_candidate)

            with col4:
                st.metric("🟢 Recommended", recommended_count)

            st.markdown("---")

            # -----------------------------
            # Candidate Ranking Table
            # -----------------------------
            display_df = pd.DataFrame([
                {
                    "Rank": index + 1,
                    "Candidate": r["candidate"],
                    "ATS Score": r["ats_score"],
                    "Skill Match (%)": r["skill_match"],
                    "Recommendation": r["recommendation"]
                }
                for index, r in enumerate(results)
            ])

            st.subheader("📊 Candidate Rankings")

            st.dataframe(
                display_df,
                use_container_width=True
            )

            st.markdown("---")

            # -----------------------------
            # Candidate Details
            # -----------------------------
            st.subheader("👤 Candidate Details")

            for candidate in results:

                with st.expander(
                    f"{candidate['candidate']} | ATS Score: {candidate['ats_score']}/100"
                ):

                    st.markdown("### 🤖 AI Summary")
                    st.write(candidate["ai_summary"])

                    st.markdown("### 🎯 Hiring Recommendation")
                    st.success(candidate["recommendation"])

                    st.markdown("### ✅ Matched Skills")
                    st.write(candidate["matched_skills"])

                    st.markdown("### ❌ Missing Skills")
                    st.write(candidate["missing_skills"])

            st.markdown("---")

            with open("Recruiter_Report.pdf", "rb") as pdf_file:

                st.download_button(
                    label="📥 Download Recruiter Report",
                    data=pdf_file,
                    file_name="Recruiter_Report.pdf",
                    mime="application/pdf"
                )

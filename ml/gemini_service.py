import os
from pathlib import Path

from dotenv import load_dotenv
import google.generativeai as genai

# -----------------------------
# Load Environment Variables
# -----------------------------
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found. Check your .env file."
    )

# -----------------------------
# Configure Gemini
# -----------------------------
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")


# =====================================================
# AI Resume Feedback
# =====================================================

def generate_feedback(
    resume_text,
    jd_text,
    ats_score,
    matched_skills,
    missing_skills,
):
    """
    Generate ATS feedback using Gemini.
    """

    prompt = f"""
You are an ATS Resume Expert.

Resume:
{resume_text}

Job Description:
{jd_text}

ATS Score:
{ats_score}

Matched Skills:
{matched_skills}

Missing Skills:
{missing_skills}

Provide your response in this format:

## Resume Strengths

## Resume Weaknesses

## Missing Skills

## Suggested Projects

## Certifications to Learn

## Final Recommendation

Keep the response concise and actionable.
"""

    response = model.generate_content(prompt)

    return response.text


# =====================================================
# AI Resume Optimizer
# =====================================================

def optimize_resume(resume_text, jd_text):
    """
    Rewrite resume content to improve ATS compatibility.
    """

    prompt = f"""
You are an expert ATS resume writer.

You will receive:

1. Resume
2. Job Description

Resume:
{resume_text}

Job Description:
{jd_text}

Your task:

Rewrite ONLY the following sections:

• Profile Summary
• Projects
• Experience
• Skills (reorder if necessary)

Rules:

1. Never invent experience.
2. Never add fake technologies.
3. Keep every statement truthful.
4. Improve grammar.
5. Improve ATS keywords.
6. Add measurable impact ONLY if already implied.
7. Keep the format professional.

Return the optimized resume in Markdown.
"""

    response = model.generate_content(prompt)

    return response.text
def candidate_summary(
    resume_text,
    jd_text,
    ats_score,
    matched_skills,
    missing_skills
):
    """
    Generate recruiter-focused candidate summary.
    """

    prompt = f"""
You are an HR Recruiter.

Candidate Resume:
{resume_text}

Job Description:
{jd_text}

ATS Score:
{ats_score}

Matched Skills:
{matched_skills}

Missing Skills:
{missing_skills}

Provide:

1. Candidate Strengths
2. Candidate Weaknesses
3. Hiring Recommendation

Limit the response to about 100 words.
Be concise and professional.
"""

    response = model.generate_content(prompt)

    return response.text
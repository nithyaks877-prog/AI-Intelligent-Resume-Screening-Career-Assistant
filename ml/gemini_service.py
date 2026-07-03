import os
import json
import re
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


# =====================================================
# AI Interview Questions
# =====================================================

def generate_interview_questions(jd_text, missing_skills):
    """
    Generate tailored interview questions based on the JD,
    as structured JSON (question, category, difficulty).
    """

    prompt = f"""
You are a technical interviewer preparing questions for a candidate
applying to this role.

Job Description:
{jd_text}

Skills the candidate is missing (focus some questions here to test
their conceptual understanding even without hands-on experience):
{missing_skills}

Generate exactly 5 interview questions relevant to this role.

Return ONLY valid JSON (no markdown, no code fences, no extra text),
in exactly this format:

[
  {{
    "question": "...",
    "category": "...",
    "difficulty": "Easy" | "Medium" | "Hard"
  }}
]
"""

    response = model.generate_content(prompt)
    return _parse_json_response(response.text)


# =====================================================
# Personalized Learning Plan
# =====================================================

def generate_learning_plan(missing_skills):
    """
    Suggest courses/resources to close the candidate's
    skill gaps, as structured JSON.
    """

    if not missing_skills:
        return []

    prompt = f"""
You are a career mentor helping a candidate close their skill gaps.

Missing skills:
{missing_skills}

For up to 3 of the most important missing skills, suggest a learning
resource for each (a real, well-known platform/course type such as
official docs, Coursera, Udemy, freeCodeCamp, or similar).

Return ONLY valid JSON (no markdown, no code fences, no extra text),
in exactly this format:

[
  {{
    "title": "...",
    "platform": "...",
    "duration": "e.g. 2 weeks"
  }}
]
"""

    response = model.generate_content(prompt)
    return _parse_json_response(response.text)


# =====================================================
# Helper: safely parse Gemini's JSON response
# =====================================================

def _parse_json_response(raw_text):
    """
    Gemini sometimes wraps JSON in ```json ... ``` code fences
    even when told not to. This strips that before parsing,
    and returns an empty list if parsing still fails
    (so the API never crashes because of a malformed AI response).
    """

    cleaned = re.sub(r"^```json|^```|```$", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return []

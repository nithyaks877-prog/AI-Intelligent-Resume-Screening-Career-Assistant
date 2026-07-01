from sentence_transformers import SentenceTransformer, util

# -----------------------------
# Load model once at import time
# (loading it per-request would be very slow)
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# How similar two skills need to be (0-1) to count as a match.
# 1.0 = identical wording. Real synonyms usually land 0.6-0.85.
# -----------------------------
SIMILARITY_THRESHOLD = 0.6


def compare_skills(resume_skills, jd_skills):
    """
    Compare resume skills with job description skills using
    semantic similarity instead of exact string matching.

    Example: "Deep Learning" in resume will now match
    "Neural Networks" in JD if they're semantically close,
    even though the words are completely different.

    Returns the SAME shape as before:
    { "matched", "missing", "extra", "match_percentage" }
    """

    if not jd_skills:
        return {
            "matched": [],
            "missing": [],
            "extra": sorted(resume_skills),
            "match_percentage": 0
        }

    if not resume_skills:
        return {
            "matched": [],
            "missing": sorted(jd_skills),
            "extra": [],
            "match_percentage": 0
        }

    # -----------------------------
    # Encode both skill lists into embeddings
    # -----------------------------
    resume_embeddings = model.encode(resume_skills, convert_to_tensor=True)
    jd_embeddings = model.encode(jd_skills, convert_to_tensor=True)

    # -----------------------------
    # Cosine similarity matrix: each JD skill vs each resume skill
    # -----------------------------
    similarity_matrix = util.cos_sim(jd_embeddings, resume_embeddings)

    matched = []
    missing = []
    used_resume_skills = set()

    for i, jd_skill in enumerate(jd_skills):
        # Find the resume skill most similar to this JD skill
        best_score, best_index = similarity_matrix[i].max(dim=0)
        best_score = best_score.item()
        best_index = best_index.item()

        if best_score >= SIMILARITY_THRESHOLD:
            matched.append(jd_skill)
            used_resume_skills.add(resume_skills[best_index])
        else:
            missing.append(jd_skill)

    extra = [
        skill for skill in resume_skills
        if skill not in used_resume_skills
    ]

    matched = sorted(matched)
    missing = sorted(missing)
    extra = sorted(extra)

    match_percentage = round((len(matched) / len(jd_skills)) * 100, 2)

    return {
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "match_percentage": match_percentage
    }

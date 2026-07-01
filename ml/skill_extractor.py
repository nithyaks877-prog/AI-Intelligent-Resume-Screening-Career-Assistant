import spacy
from spacy.matcher import PhraseMatcher

from ml.skills import TECHNICAL_SKILLS

# -----------------------------
# Load spaCy model once (expensive to load,
# so we do it at import time, not per call)
# -----------------------------
nlp = spacy.load("en_core_web_sm")

# -----------------------------
# Build the PhraseMatcher once with all known skills
# -----------------------------
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")

skill_patterns = [nlp.make_doc(skill) for skill in TECHNICAL_SKILLS]
matcher.add("SKILLS", skill_patterns)


def extract_skills(text):
    """
    Extract known technical skills from text using spaCy's
    PhraseMatcher (tokenizer-aware matching, more robust than
    raw regex against punctuation/spacing variations).

    Returns: sorted list of matched skill strings
             (same format as before).
    """
    if not text:
        return []

    doc = nlp(text)
    matches = matcher(doc)

    extracted_skills = set()

    for match_id, start, end in matches:
        span = doc[start:end]
        matched_text = span.text

        # Map back to the original casing from TECHNICAL_SKILLS
        for skill in TECHNICAL_SKILLS:
            if skill.lower() == matched_text.lower():
                extracted_skills.add(skill)
                break

    return sorted(list(extracted_skills))

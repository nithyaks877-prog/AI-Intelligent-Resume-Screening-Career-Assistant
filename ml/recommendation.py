def hiring_recommendation(ats_score):
    """
    Generate hiring recommendation based on ATS score.
    """

    if ats_score >= 85:
        return "🟢 Strongly Recommend"

    elif ats_score >= 70:
        return "🟡 Recommend"

    elif ats_score >= 55:
        return "🟠 Consider"

    else:
        return "🔴 Not Recommended"
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


def create_pdf_report(
    filename,
    ats_score,
    resume_skills,
    jd_skills,
    matched_skills,
    missing_skills,
    feedback
):

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(filename)

    story = []

    story.append(Paragraph("<b>HireSense AI</b>", styles["Title"]))

    story.append(Paragraph("ATS Analysis Report", styles["Heading1"]))

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            f"<b>Overall ATS Score:</b> {ats_score}/100",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "<b>Resume Skills</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            ", ".join(resume_skills),
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "<b>Job Description Skills</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            ", ".join(jd_skills),
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "<b>Matched Skills</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            ", ".join(matched_skills),
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "<b>Missing Skills</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            ", ".join(missing_skills),
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            "<b>AI Resume Feedback</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            feedback.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    )

    doc.build(story)
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def create_recruiter_report(filename, results):

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(filename)

    story = []

    # -----------------------------
    # Title
    # -----------------------------
    story.append(
        Paragraph(
            "<b>HireSense AI</b>",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            "Recruiter Candidate Analysis Report",
            styles["Heading1"]
        )
    )

    story.append(Spacer(1, 20))

    # -----------------------------
    # Candidate Ranking Table
    # -----------------------------
    table_data = [[
        "Rank",
        "Candidate",
        "ATS",
        "Skill Match",
        "Recommendation"
    ]]

    for index, candidate in enumerate(results):

        table_data.append([
            index + 1,
            candidate["Candidate"],
            candidate["ATS Score"],
            f'{candidate["Skill Match"]}%',
            candidate["Recommendation"]
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),

        ("GRID", (0,0), (-1,-1), 1, colors.black),

        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("BACKGROUND", (0,1), (-1,-1), colors.beige),

        ("ALIGN", (0,0), (-1,-1), "CENTER")

    ]))

    story.append(table)

    story.append(Spacer(1,20))

    # -----------------------------
    # Candidate Details
    # -----------------------------
    for index, candidate in enumerate(results):

        story.append(
            Paragraph(
                f"<b>{index+1}. {candidate['Candidate']}</b>",
                styles["Heading2"]
            )
        )

        story.append(
            Paragraph(
                f"<b>ATS Score:</b> {candidate['ATS Score']}",
                styles["BodyText"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Recommendation:</b> {candidate['Recommendation']}",
                styles["BodyText"]
            )
        )

        story.append(
            Paragraph(
                "<b>Matched Skills</b>",
                styles["Heading3"]
            )
        )

        story.append(
            Paragraph(
                ", ".join(candidate["Matched"]),
                styles["BodyText"]
            )
        )

        story.append(
            Paragraph(
                "<b>Missing Skills</b>",
                styles["Heading3"]
            )
        )

        story.append(
            Paragraph(
                ", ".join(candidate["Missing"]),
                styles["BodyText"]
            )
        )

        story.append(
            Paragraph(
                "<b>AI Summary</b>",
                styles["Heading3"]
            )
        )

        story.append(
            Paragraph(
                candidate["AI Summary"].replace("\n","<br/>"),
                styles["BodyText"]
            )
        )

        story.append(Spacer(1,20))

    doc.build(story)
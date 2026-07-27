from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os

from config import REPORT_FOLDER


class ReportGenerator:

    @staticmethod
    def _add_list(story, title, items, styles):

        story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))

        if not items:
            story.append(Paragraph("None", styles["BodyText"]))
        else:
            for item in items:
                story.append(
                    Paragraph(f"• {item}", styles["BodyText"])
                )

        story.append(Spacer(1, 0.2 * inch))

    @staticmethod
    def generate(result, filename="Resume_Comparison_Report.pdf"):

        os.makedirs(REPORT_FOLDER, exist_ok=True)

        output_path = os.path.join(REPORT_FOLDER, filename)

        document = SimpleDocTemplate(output_path)

        styles = getSampleStyleSheet()

        story = []

        # ---------------------------------
        # Title
        # ---------------------------------

        story.append(
            Paragraph(
                "<b><font size=18>Resume Comparison Report</font></b>",
                styles["Title"],
            )
        )

        story.append(Spacer(1, 0.3 * inch))

        story.append(
            Paragraph(
                f"<b>Winner:</b> {result['winner']}",
                styles["Heading1"],
            )
        )

        story.append(Spacer(1, 0.3 * inch))

        # ---------------------------------
        # Resume 1
        # ---------------------------------

        story.append(
            Paragraph(
                "<b>Resume 1 Analysis</b>",
                styles["Heading1"],
            )
        )

        scores = result["resume1"]["scores"]

        for key, value in scores.items():
            story.append(
                Paragraph(
                    f"<b>{key}:</b> {value}",
                    styles["BodyText"],
                )
            )

        story.append(Spacer(1, 0.2 * inch))

        ReportGenerator._add_list(
            story,
            "Strengths",
            result["resume1"]["strengths"],
            styles,
        )

        ReportGenerator._add_list(
            story,
            "Weaknesses",
            result["resume1"]["weaknesses"],
            styles,
        )

        ReportGenerator._add_list(
            story,
            "Suggestions",
            result["resume1"]["suggestions"],
            styles,
        )

        story.append(Spacer(1, 0.4 * inch))

        # ---------------------------------
        # Resume 2
        # ---------------------------------

        story.append(
            Paragraph(
                "<b>Resume 2 Analysis</b>",
                styles["Heading1"],
            )
        )

        scores = result["resume2"]["scores"]

        for key, value in scores.items():
            story.append(
                Paragraph(
                    f"<b>{key}:</b> {value}",
                    styles["BodyText"],
                )
            )

        story.append(Spacer(1, 0.2 * inch))

        ReportGenerator._add_list(
            story,
            "Strengths",
            result["resume2"]["strengths"],
            styles,
        )

        ReportGenerator._add_list(
            story,
            "Weaknesses",
            result["resume2"]["weaknesses"],
            styles,
        )

        ReportGenerator._add_list(
            story,
            "Suggestions",
            result["resume2"]["suggestions"],
            styles,
        )

        story.append(Spacer(1, 0.3 * inch))

        # ---------------------------------
        # Final Result
        # ---------------------------------

        story.append(
            Paragraph(
                "<b>Final Verdict</b>",
                styles["Heading1"],
            )
        )

        story.append(
            Paragraph(
                f"The better resume is <b>{result['winner']}</b> based on the ATS evaluation.",
                styles["BodyText"],
            )
        )

        document.build(story)

        return output_path
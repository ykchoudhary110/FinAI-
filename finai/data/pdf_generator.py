from pathlib import Path
from typing import Dict, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


def generate_financial_pdf_report(
    output_pdf_path: Path,
    title: str,
    summary_text: str,
    table_headers: List[str],
    table_data: List[List[str]],
):
    """
    Generates professional PDF reports using ReportLab.
    Strict implementation of Section 6 of FinAI Specification.
    """
    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#005FB8"),
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#555555"),
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#222222"),
    )

    elements = []

    # Title & Header
    elements.append(Paragraph(f"<b>FinAI</b> — {title}", title_style))
    elements.append(Paragraph("100% Offline AI-Powered Financial Assistant Report", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#005FB8"), spaceBefore=5, spaceAfter=15))

    # Narrative Summary
    elements.append(Paragraph("<b>Executive Summary</b>", styles["Heading3"]))
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 15))

    # Table Data
    if table_headers and table_data:
        full_table = [table_headers] + table_data
        t = Table(full_table, colWidths=None)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#005FB8")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9F9F9")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                    ("FONTNAME", (0, 1), (-1, -1), "Courier"),  # Monospace for numbers
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                ]
            )
        )
        elements.append(t)

    elements.append(Spacer(1, 30))
    elements.append(
        Paragraph(
            "<i>Note: This document is generated locally by FinAI for illustrative/educational tracking purposes only.</i>",
            subtitle_style,
        )
    )

    doc.build(elements)

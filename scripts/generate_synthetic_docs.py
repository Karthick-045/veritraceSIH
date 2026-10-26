import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "documents")
os.makedirs(DOCS_DIR, exist_ok=True)

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "DocTitle",
    parent=styles["Heading1"],
    fontSize=18,
    leading=22,
    textColor=colors.HexColor("#1e3a8a"),
    alignment=1, # Center
    spaceAfter=12
)
subtitle_style = ParagraphStyle(
    "DocSubTitle",
    parent=styles["Normal"],
    fontSize=11,
    leading=14,
    textColor=colors.HexColor("#475569"),
    alignment=1,
    spaceAfter=15
)
body_style = ParagraphStyle(
    "DocBody",
    parent=styles["Normal"],
    fontSize=10,
    leading=15,
    textColor=colors.HexColor("#1e293b")
)
bold_label = ParagraphStyle(
    "BoldLabel",
    parent=styles["Normal"],
    fontSize=10,
    leading=15,
    textColor=colors.HexColor("#0f172a"),
    fontName="Helvetica-Bold"
)

def create_aicte_approval_pdf(filepath: str):
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story = [
        Paragraph("ALL INDIA COUNCIL FOR TECHNICAL EDUCATION", title_style),
        Paragraph("Nelson Mandela Marg, Vasant Kunj, New Delhi-110070 | Approval Process 2025-26", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1e3a8a"), spaceAfter=20),
        Paragraph("<b>APPROVAL EXTENSION ORDER</b>", styles["Heading2"]),
        Spacer(1, 10),
        Paragraph("To,<br/>The Principal Secretary (Technical Education),<br/>Government of NCT of Delhi.", body_style),
        Spacer(1, 15),
        Paragraph("Sub: Extension of Approval for the Academic Year 2025-2026.", bold_label),
        Spacer(1, 10),
        Paragraph("Sir/Madam, In terms of the provisions under the All India Council for Technical Education (Grant of Approvals for Technical Institutions) Regulations, this Council conveys approval to:", body_style),
        Spacer(1, 15),
    ]

    table_data = [
        [Paragraph("Permanent AICTE ID", bold_label), Paragraph("1-98746210", body_style)],
        [Paragraph("Application No.", bold_label), Paragraph("AICTE/NWRO/2025-26/1-98746210", body_style)],
        [Paragraph("Name of the Institution", bold_label), Paragraph("Delhi Institute of Technology & Management", bold_label)],
        [Paragraph("Address", bold_label), Paragraph("Plot 14, Institutional Area, Sector 23, Rohini, New Delhi - 110085", body_style)],
        [Paragraph("Academic Year", bold_label), Paragraph("2025-2026", body_style)],
        [Paragraph("Total Approved Intake", bold_label), Paragraph("420", body_style)],
        [Paragraph("Total Land Area", bold_label), Paragraph("7.50 Acres", body_style)],
        [Paragraph("Date of Issue", bold_label), Paragraph("15/05/2024", body_style)],
        [Paragraph("Valid Until", bold_label), Paragraph("31/05/2026", body_style)],
    ]
    t = Table(table_data, colWidths=[200, 320])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 30))
    story.append(Paragraph("This is an electronically generated approval letter. Signature not required.", subtitle_style))
    doc.build(story)

def create_land_certificate_pdf(filepath: str):
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story = [
        Paragraph("OFFICE OF THE REVENUE DIVISIONAL OFFICER", title_style),
        Paragraph("Government of NCT of Delhi · Department of Revenue", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#047857"), spaceAfter=20),
        Paragraph("<b>LAND OCCUPANCY & TITLE VERIFICATION CERTIFICATE</b>", styles["Heading2"]),
        Spacer(1, 10),
        Paragraph("This is to certify that the institutional property described below has been inspected and title verified in accordance with statutory regulations:", body_style),
        Spacer(1, 15),
    ]

    table_data = [
        [Paragraph("Certificate Reference No.", bold_label), Paragraph("DEL/REV/2021/LAND-8812", body_style)],
        [Paragraph("Name of the Institution", bold_label), Paragraph("Delhi Inst. of Tech & Mgmt", bold_label)],
        [Paragraph("Institution ID", bold_label), Paragraph("1-98746210", body_style)],
        [Paragraph("Site Area / Campus Area", bold_label), Paragraph("7.50 Acres", body_style)],
        [Paragraph("Khasra / Plot Nos.", bold_label), Paragraph("Khasra Nos. 104/1, 104/2, Sector 23", body_style)],
        [Paragraph("Ownership Status", bold_label), Paragraph("Perpetual Educational Lease (99 Years)", body_style)],
        [Paragraph("Date of Issue", bold_label), Paragraph("15/02/2021", body_style)],
        [Paragraph("Valid Until", bold_label), Paragraph("14/02/2031", body_style)],
    ]
    t = Table(table_data, colWidths=[200, 320])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bbf7d0")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    doc.build(story)

def create_fire_safety_pdf(filepath: str):
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story = [
        Paragraph("DELHI FIRE SERVICES : HEADQUARTERS", title_style),
        Paragraph("Government of NCT of Delhi · Fire Prevention Wing", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#b91c1c"), spaceAfter=20),
        Paragraph("<b>FIRE SAFETY CLEARANCE CERTIFICATE (NOC)</b>", styles["Heading2"]),
        Spacer(1, 10),
        Paragraph("Certified that the building occupied by the educational institution has complied with the fire prevention and safety requirements under Delhi Fire Service Rules:", body_style),
        Spacer(1, 15),
    ]

    # Planted defects:
    # 1. Institution Name differs: "Delhi Public College of Engineering"
    # 2. Inverted dates: Issue Date 15/03/2024, Valid Until 14/01/2024
    # 3. Expired: Valid until 14/01/2024 is before case scrutiny date 2025-06-01
    table_data = [
        [Paragraph("NOC Dispatch No.", bold_label), Paragraph("DFS/HQ/NOC/2024/774", body_style)],
        [Paragraph("Name of the Institution", bold_label), Paragraph("Delhi Public College of Engineering", bold_label)],
        [Paragraph("Institution ID", bold_label), Paragraph("1-98746210", body_style)],
        [Paragraph("Building Blocks", bold_label), Paragraph("Academic Block A & Block B (G+4 floors)", body_style)],
        [Paragraph("Date of Issue", bold_label), Paragraph("15/03/2024", body_style)],
        [Paragraph("Valid Until", bold_label), Paragraph("14/01/2024", bold_label)], # Inverted & Expired!
    ]
    t = Table(table_data, colWidths=[200, 320])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff1f2")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecdd3")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    doc.build(story)

def create_ambiguous_date_pdf(filepath: str):
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story = [
        Paragraph("STATE ENVIRONMENTAL CLEARANCE AUTHORITY", title_style),
        Paragraph("Consent to Operate & Environmental Compliance", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=20),
        Paragraph("<b>STATUTORY CLEARANCE NOTIFICATION</b>", styles["Heading2"]),
        Spacer(1, 10),
        Paragraph("Institution: Delhi Institute of Technology & Management", bold_label),
        Paragraph("Institution ID: 1-98746210", body_style),
        Spacer(1, 10),
        # Planted Ambiguous Date: 03/04/2025 (could be 3rd April or 4th March)
        Paragraph("Date of Issue: 03/04/2025", bold_label),
        Paragraph("Academic Year: 2025-2026", body_style),
    ]
    doc.build(story)

def create_academic_conflict_pdf(filepath: str):
    doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story = [
        Paragraph("AFFILIATING UNIVERSITY BOARD", title_style),
        Paragraph("Provisional Affiliation Renewal Notice", subtitle_style),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#7c3aed"), spaceAfter=20),
        Paragraph("Institution: Delhi Institute of Technology & Management", bold_label),
        Paragraph("Institution ID: 1-98746210", body_style),
        # Planted conflict: cites 2024-2025 instead of 2025-2026
        Paragraph("Academic Year: 2024-2025", bold_label),
        Paragraph("Date of Issue: 20/06/2024", body_style),
    ]
    doc.build(story)

if __name__ == "__main__":
    print("Generating synthetic demo PDFs...")
    create_aicte_approval_pdf(os.path.join(DOCS_DIR, "demo_aicte_approval.pdf"))
    create_land_certificate_pdf(os.path.join(DOCS_DIR, "demo_land_certificate.pdf"))
    create_fire_safety_pdf(os.path.join(DOCS_DIR, "demo_fire_safety.pdf"))
    create_ambiguous_date_pdf(os.path.join(DOCS_DIR, "demo_ambiguous_date.pdf"))
    create_academic_conflict_pdf(os.path.join(DOCS_DIR, "demo_academic_conflict.pdf"))
    print(f"Generated 5 synthetic PDFs in {DOCS_DIR}")

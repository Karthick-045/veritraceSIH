import re
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import Document, DocumentPage, ExtractedField
from app.services.normalization_service import NormalizationService

PATTERNS = {
    "institution_name": [
        r"(?:Name of (?:the )?(?:Institution|College|Institute)|Institution Name)\s*(?:[:\-]\s*|\n\s*)([^\n\r,]+(?:Institute|College|University|Academy|Technology|Engineering|Tech & Mgmt)[^\n\r]*)",
        r"(?:Institution|College|Institute)\s*(?:[:\-]\s*|\n\s*)([^\n\r]+)",
        r"(?:This is to certify that|Granted to)\s+([^\n\r,]+(?:Institute|College|Technology|Engineering)[^\n\r]*)"
    ],
    "institution_id": [
        r"(?:AICTE\s*(?:File|Permanent|App)?\s*ID|Institution\s*ID|Permanent AICTE ID|Application\s*No\.?)\s*(?:[:\-]\s*|\n\s*)([A-Za-z0-9\-_/]+)",
        r"(?:File No\.?|Ref No\.?)\s*(?:[:\-]\s*|\n\s*)([A-Za-z0-9\-_/]+)"
    ],
    "academic_year": [
        r"(?:Academic Year|Session|Period)\s*(?:[:\-]?\s*|\n\s*)(\d{4}\s*[-/]\s*(?:\d{4}|\d{2}))",
        r"(?:Academic Year\s+)(\d{4}\s*[-/]\s*(?:\d{4}|\d{2}))"
    ],
    "issue_date": [
        r"(?:Date of Issue|Issue Date|Issued on|Dated)\s*(?:[:\-]?\s*|\n\s*)([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4}|[A-Za-z]+ \d{1,2}, \d{4}|\d{1,2} [A-Za-z]+ \d{4})",
        r"(?:Date)\s*(?:[:\-]\s*|\n\s*)([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4})"
    ],
    "valid_until": [
        r"(?:Valid Until|Valid Up to|Expiry Date|Validity Period|Expires on|Valid Till)\s*(?:[:\-]?\s*|\n\s*)([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4}|[A-Za-z]+ \d{1,2}, \d{4}|\d{1,2} [A-Za-z]+ \d{4})"
    ],
    "land_area": [
        r"(?:Total Land Area|Land Area|Site Area|Campus Area)\s*(?:[:\-]?\s*|\n\s*)([0-9]+(?:\.[0-9]+)?\s*(?:Acres?|sq(?:\.|\s*)meters?|sq(?:\.|\s*)ft))",
        r"([0-9]+(?:\.[0-9]+)?\s*Acres?)"
    ],
    "intake_capacity": [
        r"(?:Total Approved Intake|Intake Capacity|Approved Intake|Student Intake)\s*(?:[:\-]?\s*|\n\s*)([0-9]+)"
    ]
}

class FieldExtractor:
    @staticmethod
    def _find_bbox_for_snippet(snippet: str, layout_data: list[dict] | None) -> dict | None:
        """
        Locates the bounding box for a given snippet within page word layout_data.
        """
        if not layout_data or not snippet:
            return None

        clean_words = [w.strip(".,;:()[]{}\"'") for w in snippet.split() if w.strip(".,;:()\"'")]
        if not clean_words:
            return None

        matched_boxes = []
        for word in clean_words:
            w_lower = word.lower()
            for item in layout_data:
                item_text = item.get("text", "").strip(".,;:()[]{}\"'").lower()
                if w_lower and (w_lower in item_text or item_text in w_lower):
                    bbox = item.get("bbox")
                    if bbox:
                        matched_boxes.append(bbox)
                    break

        if not matched_boxes:
            # Fallback approximate box in upper/mid quadrant if layout exists
            return {"x0": 0.15, "y0": 0.25, "x1": 0.85, "y1": 0.35}

        min_x0 = min(b["x0"] for b in matched_boxes)
        min_y0 = min(b["y0"] for b in matched_boxes)
        max_x1 = max(b["x1"] for b in matched_boxes)
        max_y1 = max(b["y1"] for b in matched_boxes)

        # Padding for aesthetic highlight
        return {
            "x0": max(0.0, round(min_x0 - 0.01, 4)),
            "y0": max(0.0, round(min_y0 - 0.008, 4)),
            "x1": min(1.0, round(max_x1 + 0.01, 4)),
            "y1": min(1.0, round(max_y1 + 0.008, 4))
        }

    @staticmethod
    def extract_fields_from_page(db: Session, page: DocumentPage, doc: Document) -> list[ExtractedField]:
        text = page.extracted_text or ""
        layout = page.layout_data or []
        extracted = []

        for field_key, regex_list in PATTERNS.items():
            for regex in regex_list:
                match = re.search(regex, text, re.IGNORECASE)
                if match:
                    raw_val = match.group(1).strip()
                    # Quote-or-reject guard: snippet must appear verbatim in text
                    if raw_val not in text:
                        continue

                    norm_val, is_ambiguous = NormalizationService.normalize_field(field_key, raw_val)
                    bbox = FieldExtractor._find_bbox_for_snippet(raw_val, layout)

                    # Compute confidence = f(OCR confidence, pattern strength)
                    pattern_strength = 0.95
                    confidence = round(page.mean_confidence * pattern_strength, 2)

                    review_status = "extracted"
                    if confidence < settings.LOW_CONFIDENCE_THRESHOLD or is_ambiguous:
                        review_status = "needs_review"

                    field_obj = ExtractedField(
                        case_id=doc.case_id,
                        document_id=doc.id,
                        page_number=page.page_number,
                        field_key=field_key,
                        raw_value=raw_val,
                        normalized_value=norm_val,
                        confidence=confidence,
                        bbox=bbox,
                        is_ambiguous=is_ambiguous,
                        review_status=review_status,
                        extraction_method="regex_heuristic",
                        verbatim_snippet=raw_val
                    )
                    db.add(field_obj)
                    extracted.append(field_obj)
                    break  # found match for this field_key on this page

        db.commit()
        return extracted

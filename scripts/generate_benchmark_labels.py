import os
import json

LABELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "benchmark_labels")
os.makedirs(LABELS_DIR, exist_ok=True)

test_cases = [
    {
        "case_key": "CASE_BENCH_01_NAME_MISMATCH",
        "description": "Cross-document Institution Name Discrepancy (True Positive)",
        "expected_rules": ["CROSS_DOC_VALUE_MISMATCH"],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "AICTE Approval.pdf", "key": "institution_name", "raw": "National Institute of Science and Technology", "normalized": "national institute of science and technology", "confidence": 0.98},
            {"doc_id": 2, "doc_name": "Land Document.pdf", "key": "institution_name", "raw": "Metropolitan College of Engineering", "normalized": "metropolitan college of engineering", "confidence": 0.95}
        ]
    },
    {
        "case_key": "CASE_BENCH_02_NAME_ABBREVIATION_NEGATIVE",
        "description": "Institution name with common abbreviation ('Inst.' vs 'Institute') - Must NOT fire (Negative Example)",
        "expected_rules": [],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "AICTE Letter.pdf", "key": "institution_name", "raw": "Delhi Institute of Technology", "normalized": "delhi institute of technology", "confidence": 0.98},
            {"doc_id": 2, "doc_name": "Society Reg.pdf", "key": "institution_name", "raw": "Delhi Inst. of Tech", "normalized": "delhi institute of technology", "confidence": 0.96}
        ]
    },
    {
        "case_key": "CASE_BENCH_03_DATE_ORDER_INVERTED",
        "description": "Expiry date occurs before Issue date within same document (True Positive)",
        "expected_rules": ["DATE_ORDER_INVALID"],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "Fire Clearance.pdf", "key": "issue_date", "raw": "15/06/2024", "normalized": "2024-06-15", "confidence": 0.97},
            {"doc_id": 1, "doc_name": "Fire Clearance.pdf", "key": "valid_until", "raw": "10/01/2024", "normalized": "2024-01-10", "confidence": 0.95}
        ]
    },
    {
        "case_key": "CASE_BENCH_04_EXPIRED_EVIDENCE",
        "description": "Valid until date is before scrutiny review date (True Positive)",
        "expected_rules": ["EVIDENCE_EXPIRED"],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "Pollution Consent.pdf", "key": "valid_until", "raw": "31/12/2024", "normalized": "2024-12-31", "confidence": 0.96}
        ]
    },
    {
        "case_key": "CASE_BENCH_05_ACADEMIC_YEAR_MISMATCH",
        "description": "Different academic sessions cited in application bundle (True Positive)",
        "expected_rules": ["ACADEMIC_YEAR_MISMATCH"],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "AICTE Approval.pdf", "key": "academic_year", "raw": "2025-2026", "normalized": "2025-2026", "confidence": 0.99},
            {"doc_id": 2, "doc_name": "Affiliation Notice.pdf", "key": "academic_year", "raw": "2024-2025", "normalized": "2024-2025", "confidence": 0.97}
        ]
    },
    {
        "case_key": "CASE_BENCH_06_ACADEMIC_YEAR_NORMALIZATION_NEGATIVE",
        "description": "Academic years 2025-26 vs 2025-2026 normalize identically - Must NOT fire (Negative Example)",
        "expected_rules": [],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "AICTE Approval.pdf", "key": "academic_year", "raw": "2025-26", "normalized": "2025-2026", "confidence": 0.99},
            {"doc_id": 2, "doc_name": "Affiliation Letter.pdf", "key": "academic_year", "raw": "2025-2026", "normalized": "2025-2026", "confidence": 0.98}
        ]
    },
    {
        "case_key": "CASE_BENCH_07_AMBIGUOUS_DATE_ROUTING",
        "description": "Date format 03/04/2025 is ambiguous without locale - routes to review, does not accuse (True Positive)",
        "expected_rules": ["LOW_CONFIDENCE_EXTRACTION"],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "Inspection Report.pdf", "key": "issue_date", "raw": "03/04/2025", "normalized": None, "confidence": 0.90, "is_ambiguous": True}
        ]
    },
    {
        "case_key": "CASE_BENCH_08_LOW_CONFIDENCE_OCR_ROUTING",
        "description": "Blurred scan yields OCR confidence 0.48 (< 0.65 threshold) - routed to review (True Positive)",
        "expected_rules": ["LOW_CONFIDENCE_EXTRACTION"],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "Scanned Document.pdf", "key": "institution_name", "raw": "Apex Institute", "normalized": "apex institute", "confidence": 0.48}
        ]
    },
    {
        "case_key": "CASE_BENCH_09_INSTITUTION_ID_MISMATCH",
        "description": "Permanent AICTE ID differs across documents (True Positive)",
        "expected_rules": ["CROSS_DOC_VALUE_MISMATCH"],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "AICTE Approval.pdf", "key": "institution_id", "raw": "1-98746210", "normalized": "1-98746210", "confidence": 0.99},
            {"doc_id": 2, "doc_name": "Building Plan.pdf", "key": "institution_id", "raw": "1-55443322", "normalized": "1-55443322", "confidence": 0.95}
        ]
    },
    {
        "case_key": "CASE_BENCH_10_MULTIPLE_INCONSISTENCIES_COMPOUND",
        "description": "Compound case with both expired evidence and institution name mismatch",
        "expected_rules": ["CROSS_DOC_VALUE_MISMATCH", "EVIDENCE_EXPIRED"],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "Doc A.pdf", "key": "institution_name", "raw": "Global Academy of Sciences", "normalized": "global academy of sciences", "confidence": 0.95},
            {"doc_id": 2, "doc_name": "Doc B.pdf", "key": "institution_name", "raw": "Sunshine Valley Institute", "normalized": "sunshine valley institute", "confidence": 0.94},
            {"doc_id": 2, "doc_name": "Doc B.pdf", "key": "valid_until", "raw": "15/01/2025", "normalized": "2025-01-15", "confidence": 0.95}
        ]
    },
    {
        "case_key": "CASE_BENCH_11_COMPLIANT_BUNDLE_NEGATIVE",
        "description": "Completely compliant application with consistent dates and matching entities - Must NOT fire (Negative Example)",
        "expected_rules": [],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "Approval.pdf", "key": "institution_name", "raw": "Vellore College of Engineering", "normalized": "vellore college of engineering", "confidence": 0.99},
            {"doc_id": 2, "doc_name": "Land.pdf", "key": "institution_name", "raw": "Vellore College of Engineering", "normalized": "vellore college of engineering", "confidence": 0.98},
            {"doc_id": 1, "doc_name": "Approval.pdf", "key": "academic_year", "raw": "2025-2026", "normalized": "2025-2026", "confidence": 0.99},
            {"doc_id": 2, "doc_name": "Land.pdf", "key": "academic_year", "raw": "2025-2026", "normalized": "2025-2026", "confidence": 0.98},
            {"doc_id": 1, "doc_name": "Approval.pdf", "key": "issue_date", "raw": "10/01/2025", "normalized": "2025-01-10", "confidence": 0.98},
            {"doc_id": 1, "doc_name": "Approval.pdf", "key": "valid_until", "raw": "10/01/2027", "normalized": "2027-01-10", "confidence": 0.98}
        ]
    },
    {
        "case_key": "CASE_BENCH_12_LAND_AREA_DISCREPANCY",
        "description": "Declared land area differs between AICTE Application and Revenue Record (True Positive)",
        "expected_rules": ["CROSS_DOC_VALUE_MISMATCH"],
        "case_context": {"review_date": "2025-06-01"},
        "claims": [
            {"doc_id": 1, "doc_name": "AICTE Application.pdf", "key": "land_area", "raw": "10.0 Acres", "normalized": "10.00 acres", "confidence": 0.96},
            {"doc_id": 2, "doc_name": "Revenue Survey.pdf", "key": "land_area", "raw": "5.5 Acres", "normalized": "5.50 acres", "confidence": 0.95}
        ]
    }
]

for idx, case in enumerate(test_cases, 1):
    fname = f"bench_{idx:02d}_{case['case_key'].lower()}.json"
    fpath = os.path.join(LABELS_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(case, f, indent=2)

print(f"Generated {len(test_cases)} benchmark ground-truth test cases in {LABELS_DIR}")

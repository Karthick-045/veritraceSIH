from app.rules.base import Claim
from app.rules.cross_doc_value_mismatch import CrossDocValueMismatchRule
from app.rules.date_order_invalid import DateOrderInvalidRule
from app.rules.evidence_expired import EvidenceExpiredRule
from app.rules.academic_year_mismatch import AcademicYearMismatchRule
from app.rules.low_confidence_extraction import LowConfidenceExtractionRule

def test_cross_doc_mismatch_fires_on_different_names():
    rule = CrossDocValueMismatchRule()
    claims = [
        Claim(1, 1, "DocA.pdf", "general", 1, "institution_name", "Delhi Institute of Technology", "delhi institute of technology", 0.95, None, False),
        Claim(2, 2, "DocB.pdf", "general", 1, "institution_name", "Mumbai Engineering Academy", "mumbai engineering academy", 0.95, None, False)
    ]
    findings = rule.evaluate(claims, {})
    assert len(findings) == 1
    assert findings[0].rule_code == "CROSS_DOC_VALUE_MISMATCH"

def test_date_order_invalid_fires_when_expiry_before_issue():
    rule = DateOrderInvalidRule()
    claims = [
        Claim(1, 1, "NOC.pdf", "general", 1, "issue_date", "15/03/2024", "2024-03-15", 0.95, None, False),
        Claim(2, 1, "NOC.pdf", "general", 1, "valid_until", "14/01/2024", "2024-01-14", 0.95, None, False)
    ]
    findings = rule.evaluate(claims, {})
    assert len(findings) == 1
    assert findings[0].rule_code == "DATE_ORDER_INVALID"

def test_evidence_expired_fires_when_valid_before_review_date():
    rule = EvidenceExpiredRule()
    claims = [
        Claim(1, 1, "Cert.pdf", "general", 1, "valid_until", "14/01/2024", "2024-01-14", 0.95, None, False)
    ]
    findings = rule.evaluate(claims, {"review_date": "2025-06-01"})
    assert len(findings) == 1
    assert findings[0].rule_code == "EVIDENCE_EXPIRED"

def test_academic_year_negative_example_does_not_fire():
    rule = AcademicYearMismatchRule()
    claims = [
        Claim(1, 1, "Doc1.pdf", "general", 1, "academic_year", "2025-26", "2025-2026", 0.95, None, False),
        Claim(2, 2, "Doc2.pdf", "general", 1, "academic_year", "2025-2026", "2025-2026", 0.95, None, False)
    ]
    findings = rule.evaluate(claims, {})
    assert len(findings) == 0

def test_low_confidence_routing_does_not_accuse():
    rule = LowConfidenceExtractionRule()
    claims = [
        Claim(1, 1, "Doc1.pdf", "general", 1, "issue_date", "03/04/2025", None, 0.85, None, is_ambiguous=True)
    ]
    findings = rule.evaluate(claims, {})
    assert len(findings) == 1
    assert findings[0].rule_code == "LOW_CONFIDENCE_EXTRACTION"
    assert findings[0].severity == "Info"

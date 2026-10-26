from app.rules.base import Rule
from app.rules.cross_doc_value_mismatch import CrossDocValueMismatchRule
from app.rules.date_order_invalid import DateOrderInvalidRule
from app.rules.evidence_expired import EvidenceExpiredRule
from app.rules.academic_year_mismatch import AcademicYearMismatchRule
from app.rules.low_confidence_extraction import LowConfidenceExtractionRule

RULE_REGISTRY: dict[str, Rule] = {
    "CROSS_DOC_VALUE_MISMATCH": CrossDocValueMismatchRule(),
    "DATE_ORDER_INVALID": DateOrderInvalidRule(),
    "EVIDENCE_EXPIRED": EvidenceExpiredRule(),
    "ACADEMIC_YEAR_MISMATCH": AcademicYearMismatchRule(),
    "LOW_CONFIDENCE_EXTRACTION": LowConfidenceExtractionRule(),
}

def get_registered_rules() -> list[Rule]:
    return list(RULE_REGISTRY.values())

def get_rule(rule_code: str) -> Rule | None:
    return RULE_REGISTRY.get(rule_code)

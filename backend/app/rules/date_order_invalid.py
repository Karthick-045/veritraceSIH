from datetime import datetime
from app.rules.base import Rule, Claim, EvaluatedFinding

class DateOrderInvalidRule(Rule):
    rule_code = "DATE_ORDER_INVALID"
    name = "Date Order Inverted"
    version = "1.0"
    description = "Checks that an expiration or valid-until date is chronologically after the issue date within the same document."
    severity = "High"

    def evaluate(self, claims: list[Claim], case_context: dict) -> list[EvaluatedFinding]:
        findings = []
        # Group claims by document
        doc_claims_map: dict[int, list[Claim]] = {}
        for c in claims:
            doc_claims_map.setdefault(c.doc_id, []).append(c)

        for doc_id, d_claims in doc_claims_map.items():
            issue_claims = [c for c in d_claims if c.key == "issue_date" and c.usable]
            valid_claims = [c for c in d_claims if c.key == "valid_until" and c.usable]

            for iss in issue_claims:
                for val in valid_claims:
                    try:
                        dt_issue = datetime.strptime(iss.normalized, "%Y-%m-%d")
                        dt_valid = datetime.strptime(val.normalized, "%Y-%m-%d")

                        if dt_valid < dt_issue:
                            findings.append(EvaluatedFinding(
                                rule_code=self.rule_code,
                                rule_version=self.version,
                                severity=self.severity,
                                title="Inverted Date Order: Expiry Precedes Issue Date",
                                explanation=(
                                    f"In {iss.doc_name}, the validity end date '{val.raw}' ({val.normalized}) "
                                    f"is prior to the issue date '{iss.raw}' ({iss.normalized}). "
                                    f"This represents an inverted date order. Potential inconsistency; reviewer confirmation is required."
                                ),
                                evidence=[iss.as_evidence("issue_date"), val.as_evidence("valid_until")]
                            ))
                    except (ValueError, TypeError):
                        # Do not fire if dates cannot be strictly compared
                        continue

        return findings

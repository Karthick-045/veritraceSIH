from datetime import datetime
from app.rules.base import Rule, Claim, EvaluatedFinding

class EvidenceExpiredRule(Rule):
    rule_code = "EVIDENCE_EXPIRED"
    name = "Expired Certificate / Evidence"
    version = "1.0"
    description = "Checks that document validity period has not elapsed relative to the case scrutiny date."
    severity = "Medium"

    def evaluate(self, claims: list[Claim], case_context: dict) -> list[EvaluatedFinding]:
        findings = []
        review_date_val = case_context.get("review_date")
        if not review_date_val:
            return findings

        if isinstance(review_date_val, str):
            try:
                review_dt = datetime.strptime(review_date_val[:10], "%Y-%m-%d")
            except Exception:
                return findings
        elif isinstance(review_date_val, datetime):
            review_dt = review_date_val
        else:
            return findings

        valid_claims = [c for c in claims if c.key == "valid_until" and c.usable]
        for c in valid_claims:
            try:
                dt_valid = datetime.strptime(c.normalized, "%Y-%m-%d")
                if dt_valid < review_dt:
                    findings.append(EvaluatedFinding(
                        rule_code=self.rule_code,
                        rule_version=self.version,
                        severity=self.severity,
                        title="Document Validity Expired Prior to Review Date",
                        explanation=(
                            f"{c.doc_name} validity expired on '{c.raw}' ({c.normalized}), which is prior "
                            f"to the scrutiny review date ({review_dt.strftime('%Y-%m-%d')}). "
                            f"Certificate renewal or updated clearance may be required."
                        ),
                        evidence=[c.as_evidence("expired_validity")]
                    ))
            except (ValueError, TypeError):
                continue

        return findings

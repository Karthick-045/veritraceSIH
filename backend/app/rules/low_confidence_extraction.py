from app.rules.base import Rule, Claim, EvaluatedFinding

class LowConfidenceExtractionRule(Rule):
    rule_code = "LOW_CONFIDENCE_EXTRACTION"
    name = "Low Confidence / Ambiguous Value"
    version = "1.0"
    description = "Routes extracted values that are ambiguous (e.g. DD/MM vs MM/DD format without locale) or below confidence threshold to Human Review."
    severity = "Info"

    def evaluate(self, claims: list[Claim], case_context: dict) -> list[EvaluatedFinding]:
        findings = []

        for c in claims:
            reasons = []
            if c.confidence < 0.65:
                reasons.append(f"OCR/pattern confidence {c.confidence:.2f} is below 0.65 threshold")
            if c.is_ambiguous:
                reasons.append("Date format is ambiguous (e.g., DD/MM vs MM/DD) with no unambiguous locale indicator")

            if reasons:
                findings.append(EvaluatedFinding(
                    rule_code=self.rule_code,
                    rule_version=self.version,
                    severity="Info",
                    title=f"Review Needed: {c.key.replace('_', ' ').title()}",
                    explanation=(
                        f"In {c.doc_name} (Page {c.page_number}), field '{c.key}' with value '{c.raw}' "
                        f"requires officer confirmation. Reason: {'; '.join(reasons)}. "
                        f"Automated system does not assume or accuse; routed to Human Review queue."
                    ),
                    uncertainty_note="Needs human review: low confidence or ambiguous format.",
                    evidence=[c.as_evidence("ambiguous_or_low_conf")]
                ))

        return findings

from itertools import combinations
from app.rules.base import Rule, Claim, EvaluatedFinding

class AcademicYearMismatchRule(Rule):
    rule_code = "ACADEMIC_YEAR_MISMATCH"
    name = "Academic Year Discrepancy"
    version = "1.0"
    description = "Checks that academic year citations agree across application documents (e.g. 2025-26 matches 2025-2026, but conflicts with 2024-25)."
    severity = "Medium"

    def evaluate(self, claims: list[Claim], case_context: dict) -> list[EvaluatedFinding]:
        findings = []
        year_claims = [c for c in claims if c.key == "academic_year" and c.usable]

        # Group by document
        docs_map = {}
        for c in year_claims:
            if c.doc_id not in docs_map:
                docs_map[c.doc_id] = c

        doc_claims = list(docs_map.values())
        for a, b in combinations(doc_claims, 2):
            if a.normalized != b.normalized:
                findings.append(EvaluatedFinding(
                    rule_code=self.rule_code,
                    rule_version=self.version,
                    severity=self.severity,
                    title="Academic Year Conflict across Documents",
                    explanation=(
                        f"{a.doc_name} cites academic year '{a.raw}' ({a.normalized}), while "
                        f"{b.doc_name} cites '{b.raw}' ({b.normalized}). "
                        f"Potential inconsistency; reviewer confirmation is required."
                    ),
                    evidence=[a.as_evidence("source_a"), b.as_evidence("source_b")]
                ))

        return findings

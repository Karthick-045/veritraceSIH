from itertools import combinations
from rapidfuzz import fuzz
from app.rules.base import Rule, Claim, EvaluatedFinding

class CrossDocValueMismatchRule(Rule):
    rule_code = "CROSS_DOC_VALUE_MISMATCH"
    name = "Cross-Document Value Mismatch"
    version = "1.0"
    description = "Checks that critical entity values (such as Institution Name or ID) agree across uploaded documents."
    severity = "Medium"

    def evaluate(self, claims: list[Claim], case_context: dict) -> list[EvaluatedFinding]:
        findings = []
        target_keys = ["institution_name", "institution_id", "land_area", "intake_capacity"]

        for key in target_keys:
            key_claims = [c for c in claims if c.key == key and c.usable]
            # Group by document to avoid comparing claims inside the same document
            docs_map = {}
            for c in key_claims:
                if c.doc_id not in docs_map:
                    docs_map[c.doc_id] = c

            doc_claims = list(docs_map.values())
            for c1, c2 in combinations(doc_claims, 2):
                v1 = c1.normalized or c1.raw
                v2 = c2.normalized or c2.raw

                # Use fuzzy similarity for institution names
                if key == "institution_name":
                    sim = fuzz.token_set_ratio(v1, v2)
                    if sim < 85.0:  # mismatch threshold
                        severity = "Medium"
                        findings.append(EvaluatedFinding(
                            rule_code=self.rule_code,
                            rule_version=self.version,
                            severity=severity,
                            title="Institution Name Mismatch across Documents",
                            explanation=(
                                f"{c1.doc_name} (Page {c1.page_number}) states '{c1.raw}', while "
                                f"{c2.doc_name} (Page {c2.page_number}) states '{c2.raw}' "
                                f"(token similarity: {sim:.1f}%). Potential inconsistency; reviewer confirmation is required."
                            ),
                            evidence=[c1.as_evidence("source_a"), c2.as_evidence("source_b")]
                        ))
                else:
                    if v1.strip().lower() != v2.strip().lower():
                        sev = "High" if key == "institution_id" else "Medium"
                        field_title = key.replace("_", " ").title()
                        findings.append(EvaluatedFinding(
                            rule_code=self.rule_code,
                            rule_version=self.version,
                            severity=sev,
                            title=f"{field_title} Discrepancy",
                            explanation=(
                                f"{c1.doc_name} (Page {c1.page_number}) records '{c1.raw}', but "
                                f"{c2.doc_name} (Page {c2.page_number}) records '{c2.raw}'. "
                                f"Values do not match. Potential inconsistency; reviewer confirmation is required."
                            ),
                            evidence=[c1.as_evidence("source_a"), c2.as_evidence("source_b")]
                        ))

        return findings

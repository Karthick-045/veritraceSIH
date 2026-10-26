import time
import hashlib
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.models import (
    ApplicationCase, Document, ExtractedField,
    ValidationRule, AnalysisRun, Finding, FindingEvidence, AuditEvent
)
from app.rules.base import Claim
from app.rules.registry import RULE_REGISTRY

class RuleEngine:
    @staticmethod
    def compute_input_hash(docs: list[Document], fields: list[ExtractedField], rule_versions: dict[str, str]) -> str:
        tokens = []
        for d in sorted(docs, key=lambda x: x.id):
            tokens.append(f"doc:{d.id}:{d.sha256_hash}")
        for f in sorted(fields, key=lambda x: x.id):
            tokens.append(f"field:{f.id}:{f.field_key}:{f.raw_value}:{f.normalized_value}:{f.confidence}")
        for r_code in sorted(rule_versions.keys()):
            tokens.append(f"rule:{r_code}:{rule_versions[r_code]}")
        raw_str = "|".join(tokens)
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    @staticmethod
    def execute_analysis(db: Session, case_id: int, user_id: int | None = None) -> AnalysisRun:
        start_time = time.time()
        case = db.query(ApplicationCase).filter(ApplicationCase.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found")

        docs = db.query(Document).filter(Document.case_id == case_id).all()
        doc_map = {d.id: d for d in docs}
        fields = db.query(ExtractedField).filter(ExtractedField.case_id == case_id).all()

        # Get active rules from DB or fallback to registry
        db_rules = db.query(ValidationRule).filter(ValidationRule.is_active == True).all()
        if db_rules:
            active_rule_codes = {r.rule_code: r.version for r in db_rules}
        else:
            active_rule_codes = {code: r.version for code, r in RULE_REGISTRY.items()}

        input_hash = RuleEngine.compute_input_hash(docs, fields, active_rule_codes)

        # Idempotency check: if identical input hash already ran, return it
        existing_run = db.query(AnalysisRun).filter(
            AnalysisRun.case_id == case_id,
            AnalysisRun.input_hash == input_hash
        ).first()

        if existing_run and existing_run.status == "completed":
            return existing_run

        # Mark prior open findings as superseded so duplicate findings do not accumulate
        db.query(Finding).filter(
            Finding.case_id == case_id,
            Finding.reviewer_status == "pending"
        ).update({"superseded": True}, synchronize_session=False)

        # Create new AnalysisRun
        analysis_run = AnalysisRun(
            case_id=case_id,
            input_hash=input_hash,
            rule_versions=active_rule_codes,
            status="running",
            started_at=datetime.now(timezone.utc)
        )
        db.add(analysis_run)
        db.commit()
        db.refresh(analysis_run)

        # Build Claim objects
        claims: list[Claim] = []
        for f in fields:
            d = doc_map.get(f.document_id)
            d_name = d.original_filename if d else f"Doc #{f.document_id}"
            d_type = d.doc_type if d else "unknown"
            claims.append(Claim(
                field_id=f.id,
                doc_id=f.document_id,
                doc_name=d_name,
                doc_type=d_type,
                page_number=f.page_number,
                key=f.field_key,
                raw=f.raw_value,
                normalized=f.normalized_value,
                confidence=f.confidence,
                bbox=f.bbox,
                is_ambiguous=f.is_ambiguous
            ))

        case_context = {
            "case_id": case.id,
            "case_number": case.case_number,
            "institution_name": case.institution_name,
            "review_date": case.review_date
        }

        # Run each enabled rule
        all_findings = []
        for rule_code in active_rule_codes.keys():
            rule_instance = RULE_REGISTRY.get(rule_code)
            if not rule_instance:
                continue
            rule_results = rule_instance.evaluate(claims, case_context)
            for res in rule_results:
                finding = Finding(
                    case_id=case_id,
                    analysis_run_id=analysis_run.id,
                    rule_code=res.rule_code,
                    rule_version=res.rule_version,
                    severity=res.severity,
                    title=res.title,
                    explanation=res.explanation,
                    uncertainty_note=res.uncertainty_note,
                    system_status="open",
                    reviewer_status="pending",
                    superseded=False
                )
                db.add(finding)
                db.flush()

                for ev in res.evidence:
                    f_evidence = FindingEvidence(
                        finding_id=finding.id,
                        source_label=ev.get("source_label", "evidence"),
                        document_id=ev.get("document_id"),
                        page_number=ev.get("page_number", 1),
                        field_id=ev.get("field_id"),
                        field_key=ev.get("field_key", ""),
                        raw_value=ev.get("raw_value", ""),
                        normalized_value=ev.get("normalized_value"),
                        bbox=ev.get("bbox"),
                        document_name=ev.get("document_name")
                    )
                    db.add(f_evidence)

                all_findings.append(finding)

        duration_ms = int((time.time() - start_time) * 1000)
        analysis_run.status = "completed"
        analysis_run.finished_at = datetime.now(timezone.utc)
        analysis_run.duration_ms = duration_ms

        case.status = "processed"
        db.commit()

        # Audit event
        audit = AuditEvent(
            case_id=case_id,
            user_id=user_id,
            event_type="ANALYSIS_EXECUTED",
            payload={
                "run_id": analysis_run.id,
                "input_hash": input_hash,
                "findings_count": len(all_findings),
                "duration_ms": duration_ms
            }
        )
        db.add(audit)
        db.commit()

        return analysis_run

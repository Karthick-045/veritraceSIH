from collections import Counter
from datetime import date
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import ApplicationCase, Document, ExtractedField, ValidationRule
from app.rules.registry import RULE_REGISTRY
from app.schemas.schemas import (
    ApiResponse,
    ScenarioSimulationOut,
    ScenarioSimulationRequest,
    SimulationFindingOut,
    SimulationResultOut,
)
from app.services.normalization_service import NormalizationService
from app.services.rule_engine import RuleEngine

router = APIRouter(tags=["What-if Simulation"])


def _finding_signature(finding: SimulationFindingOut) -> str:
    return json.dumps(finding.model_dump(mode="json"), sort_keys=True)


def _summarize(
    findings: list[SimulationFindingOut],
    review_date: date | None,
    document_count: int,
    enabled_rule_codes: list[str],
) -> SimulationResultOut:
    return SimulationResultOut(
        review_date=review_date,
        included_document_count=document_count,
        enabled_rule_codes=enabled_rule_codes,
        finding_count=len(findings),
        findings_by_severity=dict(Counter(finding.severity for finding in findings)),
        findings=findings,
    )


@router.post(
    "/cases/{case_id}/simulate",
    response_model=ApiResponse[ScenarioSimulationOut],
)
def simulate_case(
    case_id: int,
    payload: ScenarioSimulationRequest,
    db: Session = Depends(get_db),
):
    case = db.query(ApplicationCase).filter(ApplicationCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case with ID {case_id} not found")

    documents = db.query(Document).filter(Document.case_id == case_id).all()
    fields = db.query(ExtractedField).filter(ExtractedField.case_id == case_id).all()
    document_ids = {document.id for document in documents}
    field_by_id = {field.id: field for field in fields}

    invalid_documents = set(payload.excluded_document_ids) - document_ids
    if invalid_documents:
        raise HTTPException(
            status_code=400,
            detail=f"Document IDs do not belong to case {case_id}: {sorted(invalid_documents)}",
        )

    override_ids = [override.field_id for override in payload.field_overrides]
    if len(override_ids) != len(set(override_ids)):
        raise HTTPException(status_code=400, detail="A field can only be overridden once")
    invalid_fields = set(override_ids) - field_by_id.keys()
    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Field IDs do not belong to case {case_id}: {sorted(invalid_fields)}",
        )

    db_rules = db.query(ValidationRule).filter(ValidationRule.is_active == True).all()
    baseline_rule_codes = (
        {rule.rule_code for rule in db_rules}
        if db_rules
        else set(RULE_REGISTRY)
    )
    scenario_rule_codes = (
        set(payload.enabled_rule_codes)
        if payload.enabled_rule_codes is not None
        else baseline_rule_codes
    )
    unknown_rules = scenario_rule_codes - RULE_REGISTRY.keys()
    if unknown_rules:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown rule codes: {sorted(unknown_rules)}",
        )

    included_documents = [
        document for document in documents
        if document.id not in set(payload.excluded_document_ids)
    ]
    included_document_ids = {document.id for document in included_documents}
    scenario_fields = [
        field for field in fields if field.document_id in included_document_ids
    ]

    scenario_claims = RuleEngine.build_claims(included_documents, scenario_fields)
    claims_by_id = {claim.field_id: claim for claim in scenario_claims}
    for override in payload.field_overrides:
        field = field_by_id[override.field_id]
        if field.document_id not in included_document_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot override field {override.field_id} from an excluded document",
            )
        claim = claims_by_id[override.field_id]
        claim.raw = override.raw_value
        claim.normalized, claim.is_ambiguous = NormalizationService.normalize_field(
            claim.key, override.raw_value
        )

    baseline_review_date = case.review_date.date() if case.review_date else None
    scenario_review_date = payload.review_date or baseline_review_date
    scenario_review_date_value = (
        scenario_review_date.isoformat() if scenario_review_date else None
    )
    baseline_docs = documents
    baseline_fields = fields
    baseline_claims = RuleEngine.build_claims(baseline_docs, baseline_fields)

    baseline_results = RuleEngine.evaluate_claims(
        baseline_claims,
        {"case_id": case.id, "case_number": case.case_number,
         "institution_name": case.institution_name, "review_date": case.review_date},
        baseline_rule_codes,
    )
    scenario_results = RuleEngine.evaluate_claims(
        scenario_claims,
        {"case_id": case.id, "case_number": case.case_number,
         "institution_name": case.institution_name,
         "review_date": scenario_review_date_value},
        scenario_rule_codes,
    )

    baseline_findings = [
        SimulationFindingOut(
            rule_code=finding.rule_code,
            title=finding.title,
            severity=finding.severity,
            explanation=finding.explanation,
            evidence=finding.evidence,
        )
        for finding in baseline_results
    ]
    scenario_findings = [
        SimulationFindingOut(
            rule_code=finding.rule_code,
            title=finding.title,
            severity=finding.severity,
            explanation=finding.explanation,
            evidence=finding.evidence,
        )
        for finding in scenario_results
    ]

    baseline_counts = Counter(map(_finding_signature, baseline_findings))
    scenario_counts = Counter(map(_finding_signature, scenario_findings))
    baseline_by_signature = {_finding_signature(finding): finding for finding in baseline_findings}
    scenario_by_signature = {_finding_signature(finding): finding for finding in scenario_findings}
    added = [
        scenario_by_signature[signature]
        for signature, count in (scenario_counts - baseline_counts).items()
        for _ in range(count)
    ]
    resolved = [
        baseline_by_signature[signature]
        for signature, count in (baseline_counts - scenario_counts).items()
        for _ in range(count)
    ]

    return ApiResponse(
        data=ScenarioSimulationOut(
            baseline=_summarize(
                baseline_findings,
                baseline_review_date,
                len(documents),
                sorted(baseline_rule_codes),
            ),
            scenario=_summarize(
                scenario_findings,
                scenario_review_date,
                len(included_documents),
                sorted(scenario_rule_codes),
            ),
            added_findings=added,
            resolved_findings=resolved,
        )
    )

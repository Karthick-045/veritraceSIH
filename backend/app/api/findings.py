from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.rbac import get_current_user_optional, get_current_user
from app.models.models import Finding, FindingEvidence, Document, User
from app.schemas.schemas import FindingOut, EvidenceItemOut, ReviewActionCreate, ApiResponse
from app.services.review_service import ReviewService

router = APIRouter(tags=["Findings"])

@router.get("/cases/{case_id}/findings", response_model=ApiResponse[list[FindingOut]])
def list_case_findings(case_id: int, include_superseded: bool = False, db: Session = Depends(get_db)):
    query = db.query(Finding).filter(Finding.case_id == case_id)
    if not include_superseded:
        query = query.filter(Finding.superseded == False)
    findings = query.order_by(Finding.id.asc()).all()

    # Pre-fetch document names
    doc_map = {d.id: d.original_filename for d in db.query(Document).filter(Document.case_id == case_id).all()}

    out = []
    for f in findings:
        evidence_items = []
        for ev in f.evidence_items:
            evidence_items.append(EvidenceItemOut(
                id=ev.id,
                source_label=ev.source_label,
                document_id=ev.document_id,
                page_number=ev.page_number,
                field_key=ev.field_key,
                raw_value=ev.raw_value,
                normalized_value=ev.normalized_value,
                bbox=ev.bbox,
                document_name=ev.document_name or doc_map.get(ev.document_id, "Document")
            ))
        f_out = FindingOut(
            id=f.id,
            case_id=f.case_id,
            analysis_run_id=f.analysis_run_id,
            rule_code=f.rule_code,
            rule_version=f.rule_version,
            severity=f.severity,
            title=f.title,
            explanation=f.explanation,
            uncertainty_note=f.uncertainty_note,
            system_status=f.system_status,
            reviewer_status=f.reviewer_status,
            superseded=f.superseded,
            created_at=f.created_at,
            evidence_items=evidence_items
        )
        out.append(f_out)
    return ApiResponse(data=out)

@router.get("/findings/{finding_id}", response_model=ApiResponse[FindingOut])
def get_finding(finding_id: int, db: Session = Depends(get_db)):
    f = db.query(Finding).filter(Finding.id == finding_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")

    evidence_items = []
    for ev in f.evidence_items:
        evidence_items.append(EvidenceItemOut(
            id=ev.id,
            source_label=ev.source_label,
            document_id=ev.document_id,
            page_number=ev.page_number,
            field_key=ev.field_key,
            raw_value=ev.raw_value,
            normalized_value=ev.normalized_value,
            bbox=ev.bbox,
            document_name=ev.document_name
        ))
    f_out = FindingOut(
        id=f.id,
        case_id=f.case_id,
        analysis_run_id=f.analysis_run_id,
        rule_code=f.rule_code,
        rule_version=f.rule_version,
        severity=f.severity,
        title=f.title,
        explanation=f.explanation,
        uncertainty_note=f.uncertainty_note,
        system_status=f.system_status,
        reviewer_status=f.reviewer_status,
        superseded=f.superseded,
        created_at=f.created_at,
        evidence_items=evidence_items
    )
    return ApiResponse(data=f_out)

@router.post("/findings/{finding_id}/review", response_model=ApiResponse[FindingOut])
def review_finding(
    finding_id: int,
    payload: ReviewActionCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else 1
    updated = ReviewService.submit_review(
        db=db,
        finding_id=finding_id,
        decision=payload.decision,
        comment=payload.comment,
        user_id=user_id
    )
    return ApiResponse(data=FindingOut.model_validate(updated))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.rbac import get_current_user
from app.models.models import ExtractedField, FieldCorrection, Document, AuditEvent, User
from app.schemas.schemas import ExtractedFieldOut, FieldCorrectionCreate, ApiResponse
from app.services.normalization_service import NormalizationService

router = APIRouter(tags=["Fields"])

@router.get("/cases/{case_id}/fields", response_model=ApiResponse[list[ExtractedFieldOut]])
def get_case_fields(case_id: int, db: Session = Depends(get_db)):
    fields = db.query(ExtractedField).filter(ExtractedField.case_id == case_id).all()
    docs = {d.id: d.original_filename for d in db.query(Document).filter(Document.case_id == case_id).all()}

    out = []
    for f in fields:
        item = ExtractedFieldOut(
            id=f.id,
            case_id=f.case_id,
            document_id=f.document_id,
            page_number=f.page_number,
            field_key=f.field_key,
            raw_value=f.raw_value,
            normalized_value=f.normalized_value,
            confidence=f.confidence,
            bbox=f.bbox,
            is_ambiguous=f.is_ambiguous,
            review_status=f.review_status,
            extraction_method=f.extraction_method,
            verbatim_snippet=f.verbatim_snippet,
            document_name=docs.get(f.document_id)
        )
        out.append(item)
    return ApiResponse(data=out)

@router.post("/fields/{field_id}/correct", response_model=ApiResponse[ExtractedFieldOut])
def correct_field(
    field_id: int,
    payload: FieldCorrectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    field = db.query(ExtractedField).filter(ExtractedField.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Extracted field not found")

    orig_val = field.raw_value
    corr_val = payload.corrected_value.strip()

    # Save provenance correction row
    correction = FieldCorrection(
        field_id=field.id,
        original_value=orig_val,
        corrected_value=corr_val,
        reason=payload.reason,
        corrected_by=current_user.id
    )
    db.add(correction)

    # Re-normalize corrected value
    norm_val, is_ambiguous = NormalizationService.normalize_field(field.field_key, corr_val)

    field.raw_value = corr_val
    field.normalized_value = norm_val
    field.confidence = 1.0  # human confirmed
    field.is_ambiguous = is_ambiguous
    field.review_status = "corrected"

    # Audit event
    audit = AuditEvent(
        case_id=field.case_id,
        user_id=current_user.id,
        event_type="FIELD_CORRECTED",
        payload={
            "field_id": field.id,
            "field_key": field.field_key,
            "original_value": orig_val,
            "corrected_value": corr_val,
            "reason": payload.reason
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(field)

    return ApiResponse(data=ExtractedFieldOut.model_validate(field))

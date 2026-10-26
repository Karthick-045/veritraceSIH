from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import AuditEventOut, ApiResponse
from app.services.audit_service import AuditService

router = APIRouter(tags=["Audit"])

@router.get("/cases/{case_id}/audit", response_model=ApiResponse[list[AuditEventOut]])
def get_case_audit_trail(case_id: int, db: Session = Depends(get_db)):
    events = AuditService.get_case_audit_trail(db, case_id)
    return ApiResponse(data=[AuditEventOut.model_validate(e) for e in events])

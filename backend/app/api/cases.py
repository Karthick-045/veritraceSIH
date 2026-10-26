from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.rbac import get_current_user_optional
from app.models.models import ApplicationCase, Document, Finding, User, AuditEvent
from app.schemas.schemas import CaseCreate, CaseUpdate, CaseOut, ApiResponse

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.get("", response_model=ApiResponse[list[CaseOut]])
def list_cases(db: Session = Depends(get_db)):
    cases = db.query(ApplicationCase).order_by(ApplicationCase.created_at.desc()).all()
    out = []
    for c in cases:
        doc_count = db.query(Document).filter(Document.case_id == c.id).count()
        finding_count = db.query(Finding).filter(Finding.case_id == c.id, Finding.superseded == False).count()
        item = CaseOut(
            id=c.id,
            case_number=c.case_number,
            title=c.title,
            institution_name=c.institution_name,
            status=c.status,
            review_date=c.review_date,
            assigned_to_id=c.assigned_to_id,
            created_at=c.created_at,
            updated_at=c.updated_at,
            document_count=doc_count,
            finding_count=finding_count
        )
        out.append(item)
    return ApiResponse(data=out)

@router.post("", response_model=ApiResponse[CaseOut], status_code=status.HTTP_201_CREATED)
def create_case(payload: CaseCreate, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)):
    existing = db.query(ApplicationCase).filter(ApplicationCase.case_number == payload.case_number.strip()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Case with number '{payload.case_number}' already exists."
        )

    case = ApplicationCase(
        case_number=payload.case_number.strip(),
        title=payload.title.strip(),
        institution_name=payload.institution_name.strip(),
        status="pending",
        review_date=payload.review_date,
        assigned_to_id=current_user.id if current_user else None
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    # Audit
    audit = AuditEvent(
        case_id=case.id,
        user_id=current_user.id if current_user else None,
        event_type="CASE_CREATED",
        payload={
            "case_number": case.case_number,
            "title": case.title,
            "institution_name": case.institution_name
        }
    )
    db.add(audit)
    db.commit()

    return ApiResponse(data=CaseOut.model_validate(case))

@router.get("/{id}", response_model=ApiResponse[CaseOut])
def get_case(id: int, db: Session = Depends(get_db)):
    case = db.query(ApplicationCase).filter(ApplicationCase.id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case with ID {id} not found")

    doc_count = db.query(Document).filter(Document.case_id == case.id).count()
    finding_count = db.query(Finding).filter(Finding.case_id == case.id, Finding.superseded == False).count()
    item = CaseOut(
        id=case.id,
        case_number=case.case_number,
        title=case.title,
        institution_name=case.institution_name,
        status=case.status,
        review_date=case.review_date,
        assigned_to_id=case.assigned_to_id,
        created_at=case.created_at,
        updated_at=case.updated_at,
        document_count=doc_count,
        finding_count=finding_count
    )
    return ApiResponse(data=item)

@router.patch("/{id}", response_model=ApiResponse[CaseOut])
def update_case(id: int, payload: CaseUpdate, db: Session = Depends(get_db)):
    case = db.query(ApplicationCase).filter(ApplicationCase.id == id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case with ID {id} not found")

    if payload.title is not None:
        case.title = payload.title.strip()
    if payload.institution_name is not None:
        case.institution_name = payload.institution_name.strip()
    if payload.status is not None:
        case.status = payload.status
    if payload.review_date is not None:
        case.review_date = payload.review_date
    if payload.assigned_to_id is not None:
        case.assigned_to_id = payload.assigned_to_id

    db.commit()
    db.refresh(case)
    return ApiResponse(data=CaseOut.model_validate(case))

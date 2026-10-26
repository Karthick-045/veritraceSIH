import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.rbac import get_current_user_optional
from app.models.models import Document, DocumentPage, User
from app.schemas.schemas import DocumentOut, DocumentPageOut, ApiResponse
from app.services.document_service import DocumentService
from app.services.extraction_service import ExtractionService
from app.services.field_extractor import FieldExtractor

router = APIRouter(tags=["Documents"])

@router.post("/cases/{case_id}/documents", response_model=ApiResponse[DocumentOut])
def upload_document(
    case_id: int,
    file: UploadFile = File(...),
    doc_type: str = Form("general"),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    # 1. Save document
    doc = DocumentService.save_and_create_document(
        db=db,
        case_id=case_id,
        file=file,
        doc_type=doc_type,
        user_id=user_id
    )

    # 2. Extract text, layout, and page images
    pages = ExtractionService.extract_document(db=db, document=doc, user_id=user_id)

    # 3. Extract fields from each page
    for p in pages:
        FieldExtractor.extract_fields_from_page(db=db, page=p, doc=doc)

    return ApiResponse(data=DocumentOut.model_validate(doc))

@router.get("/cases/{case_id}/documents", response_model=ApiResponse[list[DocumentOut]])
def list_case_documents(case_id: int, db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.case_id == case_id).all()
    return ApiResponse(data=[DocumentOut.model_validate(d) for d in docs])

@router.get("/documents/{document_id}/pages/{page_num}", response_model=ApiResponse[DocumentPageOut])
def get_document_page(document_id: int, page_num: int, db: Session = Depends(get_db)):
    page = db.query(DocumentPage).filter(
        DocumentPage.document_id == document_id,
        DocumentPage.page_number == page_num
    ).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    has_img = bool(page.image_path and os.path.exists(page.image_path))
    out = DocumentPageOut(
        page_number=page.page_number,
        extracted_text=page.extracted_text,
        ocr_engine=page.ocr_engine,
        mean_confidence=page.mean_confidence,
        layout_data=page.layout_data,
        has_image=has_img
    )
    return ApiResponse(data=out)

@router.get("/documents/{document_id}/pages/{page_num}/image")
def get_document_page_image(document_id: int, page_num: int, db: Session = Depends(get_db)):
    page = db.query(DocumentPage).filter(
        DocumentPage.document_id == document_id,
        DocumentPage.page_number == page_num
    ).first()
    if not page or not page.image_path or not os.path.exists(page.image_path):
        raise HTTPException(status_code=404, detail="Page image not found")

    with open(page.image_path, "rb") as f:
        img_bytes = f.read()

    return Response(content=img_bytes, media_type="image/png")

@router.post("/documents/{document_id}/reprocess", response_model=ApiResponse[DocumentOut])
def reprocess_document(document_id: int, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    pages = ExtractionService.extract_document(db=db, document=doc, user_id=current_user.id if current_user else None)
    for p in pages:
        FieldExtractor.extract_fields_from_page(db=db, page=p, doc=doc)

    return ApiResponse(data=DocumentOut.model_validate(doc))

import os
import uuid
import hashlib
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import Document, ApplicationCase, AuditEvent

ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/tiff": ".tif"
}
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB

class DocumentService:
    @staticmethod
    def save_and_create_document(
        db: Session,
        case_id: int,
        file: UploadFile,
        doc_type: str = "general",
        user_id: int | None = None
    ) -> Document:
        case = db.query(ApplicationCase).filter(ApplicationCase.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail=f"Case with ID {case_id} not found")

        content = file.file.read()
        file_size = len(content)
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed size of 25MB")

        mime_type = file.content_type or "application/octet-stream"
        sha256_hash = hashlib.sha256(content).hexdigest()

        # Generate unique storage filename in private storage
        ext = os.path.splitext(file.filename or "")[1] or ".bin"
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        case_storage_dir = os.path.join(settings.STORAGE_DIR, f"case_{case_id}")
        os.makedirs(case_storage_dir, exist_ok=True)
        file_path = os.path.join(case_storage_dir, stored_filename)

        with open(file_path, "wb") as f:
            f.write(content)

        doc = Document(
            case_id=case_id,
            doc_type=doc_type,
            file_path=file_path,
            original_filename=file.filename or "unknown",
            mime_type=mime_type,
            file_size_bytes=file_size,
            sha256_hash=sha256_hash,
            status="uploaded"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Audit event
        audit = AuditEvent(
            case_id=case_id,
            user_id=user_id,
            event_type="DOC_UPLOADED",
            payload={
                "document_id": doc.id,
                "filename": doc.original_filename,
                "doc_type": doc_type,
                "sha256": sha256_hash,
                "size_bytes": file_size
            }
        )
        db.add(audit)
        db.commit()

        return doc

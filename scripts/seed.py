import os
import sys
import shutil
from datetime import datetime, timezone

# Ensure backend app in pythonpath
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.models import (
    User, ApplicationCase, Document, ValidationRule, AuditEvent
)
from app.rules.registry import RULE_REGISTRY
from app.services.extraction_service import ExtractionService
from app.services.field_extractor import FieldExtractor
from app.services.rule_engine import RuleEngine

def run_seed():
    print("Initializing Database schema...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Users
        admin = db.query(User).filter(User.email == "admin@veritrace.gov.in").first()
        if not admin:
            admin = User(
                email="admin@veritrace.gov.in",
                hashed_password=get_password_hash("admin123"),
                full_name="Chief Scrutiny Officer (Admin)",
                role="admin"
            )
            db.add(admin)

        reviewer = db.query(User).filter(User.email == "officer@veritrace.gov.in").first()
        if not reviewer:
            reviewer = User(
                email="officer@veritrace.gov.in",
                hashed_password=get_password_hash("officer123"),
                full_name="Verification Reviewer (Officer)",
                role="reviewer"
            )
            db.add(reviewer)
        db.commit()
        db.refresh(admin)
        db.refresh(reviewer)
        print("[OK] Users seeded: admin@veritrace.gov.in / officer@veritrace.gov.in")

        # 2. Validation Rules
        for r in RULE_REGISTRY.values():
            existing = db.query(ValidationRule).filter(ValidationRule.rule_code == r.rule_code).first()
            if not existing:
                db_rule = ValidationRule(
                    rule_code=r.rule_code,
                    name=r.name,
                    description=r.description,
                    version=r.version,
                    is_active=True,
                    severity=r.severity
                )
                db.add(db_rule)
        db.commit()
        print("[OK] 5 Deterministic Validation Rules registered")

        # 3. Demo Case 1: CASE-DEMO-01 (Signature Contradiction Flow)
        case_demo_1 = db.query(ApplicationCase).filter(ApplicationCase.case_number == "CASE-DEMO-01").first()
        if not case_demo_1:
            case_demo_1 = ApplicationCase(
                case_number="CASE-DEMO-01",
                title="Delhi Institute of Technology & Management - EoA Bundle",
                institution_name="Delhi Institute of Technology & Management",
                status="pending",
                review_date=datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc),
                assigned_to_id=reviewer.id
            )
            db.add(case_demo_1)
            db.commit()
            db.refresh(case_demo_1)

            # Audit
            db.add(AuditEvent(
                case_id=case_demo_1.id,
                user_id=admin.id,
                event_type="CASE_CREATED",
                payload={"case_number": "CASE-DEMO-01", "title": case_demo_1.title}
            ))
            db.commit()

            # Attach 3 documents
            docs_info = [
                ("demo_aicte_approval.pdf", "AICTE Approval Letter", "aicte_approval"),
                ("demo_land_certificate.pdf", "Land Occupancy Certificate", "land_certificate"),
                ("demo_fire_safety.pdf", "Fire Safety NOC Clearance", "fire_safety_noc"),
            ]
            sample_docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "documents")
            storage_case_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", f"case_{case_demo_1.id}")
            os.makedirs(storage_case_dir, exist_ok=True)

            for fname, title, dtype in docs_info:
                src_path = os.path.join(sample_docs_dir, fname)
                if os.path.exists(src_path):
                    dst_path = os.path.join(storage_case_dir, fname)
                    shutil.copyfile(src_path, dst_path)

                    with open(dst_path, "rb") as f:
                        content = f.read()
                    import hashlib
                    sha256 = hashlib.sha256(content).hexdigest()

                    doc = Document(
                        case_id=case_demo_1.id,
                        doc_type=dtype,
                        file_path=dst_path,
                        original_filename=fname,
                        mime_type="application/pdf",
                        file_size_bytes=len(content),
                        sha256_hash=sha256,
                        status="uploaded"
                    )
                    db.add(doc)
                    db.commit()
                    db.refresh(doc)

                    # Extract pages & layout
                    pages = ExtractionService.extract_document(db, doc, user_id=reviewer.id)
                    # Extract fields
                    for p in pages:
                        FieldExtractor.extract_fields_from_page(db, p, doc)

            # Run deterministic rule engine
            print("Running RuleEngine on CASE-DEMO-01...")
            run = RuleEngine.execute_analysis(db, case_demo_1.id, user_id=reviewer.id)
            print(f"[OK] CASE-DEMO-01 processed successfully (Run ID: {run.id}, Status: {run.status})")

        # 4. Demo Case 2: CASE-DEMO-02 (Ambiguous Date / Responsible AI)
        case_demo_2 = db.query(ApplicationCase).filter(ApplicationCase.case_number == "CASE-DEMO-02").first()
        if not case_demo_2:
            case_demo_2 = ApplicationCase(
                case_number="CASE-DEMO-02",
                title="State Environmental Clearance - Ambiguous Date Scrutiny",
                institution_name="Delhi Institute of Technology & Management",
                status="pending",
                review_date=datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc),
                assigned_to_id=reviewer.id
            )
            db.add(case_demo_2)
            db.commit()
            db.refresh(case_demo_2)

            sample_docs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_data", "documents")
            storage_case_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", f"case_{case_demo_2.id}")
            os.makedirs(storage_case_dir, exist_ok=True)

            fname = "demo_ambiguous_date.pdf"
            src_path = os.path.join(sample_docs_dir, fname)
            if os.path.exists(src_path):
                dst_path = os.path.join(storage_case_dir, fname)
                shutil.copyfile(src_path, dst_path)
                with open(dst_path, "rb") as f:
                    content = f.read()
                import hashlib
                sha256 = hashlib.sha256(content).hexdigest()

                doc = Document(
                    case_id=case_demo_2.id,
                    doc_type="statutory_clearance",
                    file_path=dst_path,
                    original_filename=fname,
                    mime_type="application/pdf",
                    file_size_bytes=len(content),
                    sha256_hash=sha256,
                    status="uploaded"
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)
                pages = ExtractionService.extract_document(db, doc, user_id=reviewer.id)
                for p in pages:
                    FieldExtractor.extract_fields_from_page(db, p, doc)

                RuleEngine.execute_analysis(db, case_demo_2.id, user_id=reviewer.id)
                print("[OK] CASE-DEMO-02 processed successfully")

    finally:
        db.close()

if __name__ == "__main__":
    run_seed()

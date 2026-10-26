from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, Index, JSON, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="reviewer")  # admin | reviewer
    created_at = Column(DateTime, default=utc_now, nullable=False)

    assigned_cases = relationship("ApplicationCase", back_populates="assigned_to")
    review_decisions = relationship("ReviewDecision", back_populates="reviewer")
    corrections = relationship("FieldCorrection", back_populates="reviewer")


class ApplicationCase(Base):
    __tablename__ = "application_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(100), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    institution_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="pending")  # pending | processing | completed | reviewed
    review_date = Column(DateTime, nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    assigned_to = relationship("User", back_populates="assigned_cases")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    extracted_fields = relationship("ExtractedField", back_populates="case", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="case", cascade="all, delete-orphan")
    findings = relationship("Finding", back_populates="case", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="case", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("application_cases.id"), nullable=False, index=True)
    doc_type = Column(String(100), nullable=False, default="general")  # aicte_approval, land_certificate, fire_safety, etc.
    file_path = Column(String(500), nullable=False)
    original_filename = Column(String(255), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="uploaded")  # uploaded | extracted | failed
    created_at = Column(DateTime, default=utc_now, nullable=False)

    case = relationship("ApplicationCase", back_populates="documents")
    pages = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    extracted_fields = relationship("ExtractedField", back_populates="document", cascade="all, delete-orphan")


class DocumentPage(Base):
    __tablename__ = "document_pages"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False)
    extracted_text = Column(Text, nullable=False, default="")
    ocr_engine = Column(String(50), nullable=False, default="PyMuPDF")
    mean_confidence = Column(Float, nullable=False, default=1.0)
    layout_data = Column(JSON, nullable=True)  # words, bboxes: [{text, x0, y0, x1, y1, conf}]
    image_path = Column(String(500), nullable=True)  # rendered page PNG for viewing
    created_at = Column(DateTime, default=utc_now, nullable=False)

    document = relationship("Document", back_populates="pages")


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("application_cases.id"), nullable=False, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    page_number = Column(Integer, nullable=False, default=1)
    field_key = Column(String(100), nullable=False, index=True)  # e.g., institution_name, academic_year, issue_date, valid_until
    raw_value = Column(Text, nullable=False)
    normalized_value = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False, default=1.0)
    bbox = Column(JSON, nullable=True)  # {x0, y0, x1, y1} normalized 0..1
    is_ambiguous = Column(Boolean, nullable=False, default=False)
    review_status = Column(String(50), nullable=False, default="extracted")  # extracted | needs_review | corrected
    extraction_method = Column(String(50), nullable=False, default="regex_heuristic")
    verbatim_snippet = Column(Text, nullable=True)  # Quote-or-reject guard text
    created_at = Column(DateTime, default=utc_now, nullable=False)

    case = relationship("ApplicationCase", back_populates="extracted_fields")
    document = relationship("Document", back_populates="extracted_fields")
    corrections = relationship("FieldCorrection", back_populates="field", cascade="all, delete-orphan")


class FieldCorrection(Base):
    __tablename__ = "field_corrections"

    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(Integer, ForeignKey("extracted_fields.id"), nullable=False, index=True)
    original_value = Column(Text, nullable=False)
    corrected_value = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    corrected_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    field = relationship("ExtractedField", back_populates="corrections")
    reviewer = relationship("User", back_populates="corrections")


class ValidationRule(Base):
    __tablename__ = "validation_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_code = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    version = Column(String(20), nullable=False, default="1.0")
    is_active = Column(Boolean, nullable=False, default=True)
    severity = Column(String(50), nullable=False, default="Medium")  # Info, Low, Medium, High, Critical
    parameters = Column(JSON, nullable=True)


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("application_cases.id"), nullable=False, index=True)
    input_hash = Column(String(64), nullable=False)
    rule_versions = Column(JSON, nullable=False)  # {"CROSS_DOC_VALUE_MISMATCH": "1.0", ...}
    status = Column(String(50), nullable=False, default="running")  # running | completed | failed
    started_at = Column(DateTime, default=utc_now, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("case_id", "input_hash", name="uq_case_input_hash"),
    )

    case = relationship("ApplicationCase", back_populates="analysis_runs")
    findings = relationship("Finding", back_populates="analysis_run")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("application_cases.id"), nullable=False, index=True)
    analysis_run_id = Column(Integer, ForeignKey("analysis_runs.id"), nullable=True, index=True)
    rule_code = Column(String(100), nullable=False)
    rule_version = Column(String(20), nullable=False, default="1.0")
    severity = Column(String(50), nullable=False)  # Info, Low, Medium, High, Critical
    title = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    uncertainty_note = Column(Text, nullable=True, default="Potential inconsistency; reviewer confirmation is required.")
    system_status = Column(String(50), nullable=False, default="open")  # original automated state, never overwritten
    reviewer_status = Column(String(50), nullable=False, default="pending")  # pending | confirmed | dismissed | needs_more_evidence | resolved
    superseded = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    case = relationship("ApplicationCase", back_populates="findings")
    analysis_run = relationship("AnalysisRun", back_populates="findings")
    evidence_items = relationship("FindingEvidence", back_populates="finding", cascade="all, delete-orphan")
    decisions = relationship("ReviewDecision", back_populates="finding", cascade="all, delete-orphan")


class FindingEvidence(Base):
    __tablename__ = "finding_evidence"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id"), nullable=False, index=True)
    source_label = Column(String(100), nullable=False)  # source_a | source_b | single_source
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False, default=1)
    field_id = Column(Integer, ForeignKey("extracted_fields.id"), nullable=True)
    field_key = Column(String(100), nullable=False)
    raw_value = Column(Text, nullable=False)
    normalized_value = Column(Text, nullable=True)
    bbox = Column(JSON, nullable=True)  # {x0, y0, x1, y1}
    document_name = Column(String(255), nullable=True)

    finding = relationship("Finding", back_populates="evidence_items")


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(Integer, ForeignKey("findings.id"), nullable=False, index=True)
    decision = Column(String(50), nullable=False)  # confirmed | dismissed | needs_more_evidence | resolved
    comment = Column(Text, nullable=False)  # Mandatory reason for audit
    decided_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    finding = relationship("Finding", back_populates="decisions")
    reviewer = relationship("User", back_populates="review_decisions")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("application_cases.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_type = Column(String(100), nullable=False)  # CASE_CREATED, DOC_UPLOADED, OCR_EXTRACTED, ANALYSIS_EXECUTED, FINDING_REVIEWED, FIELD_CORRECTED
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False, index=True)

    case = relationship("ApplicationCase", back_populates="audit_events")


class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    id = Column(Integer, primary_key=True, index=True)
    total_cases = Column(Integer, nullable=False, default=0)
    precision = Column(Float, nullable=False, default=0.0)
    recall = Column(Float, nullable=False, default=0.0)
    f1_score = Column(Float, nullable=False, default=0.0)
    tp_count = Column(Integer, nullable=False, default=0)
    fp_count = Column(Integer, nullable=False, default=0)
    fn_count = Column(Integer, nullable=False, default=0)
    duration_ms = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    case_results = relationship("BenchmarkCaseResult", back_populates="benchmark_run", cascade="all, delete-orphan")


class BenchmarkCaseResult(Base):
    __tablename__ = "benchmark_case_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("benchmark_runs.id"), nullable=False, index=True)
    case_key = Column(String(100), nullable=False)
    expected_rules = Column(JSON, nullable=False)  # ["CROSS_DOC_VALUE_MISMATCH", ...]
    detected_rules = Column(JSON, nullable=False)
    tp = Column(Integer, nullable=False, default=0)
    fp = Column(Integer, nullable=False, default=0)
    fn = Column(Integer, nullable=False, default=0)
    duration_ms = Column(Integer, nullable=False, default=0)

    benchmark_run = relationship("BenchmarkRun", back_populates="case_results")

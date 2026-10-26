from datetime import datetime
from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field, EmailStr

T = TypeVar("T")

class ErrorDetail(BaseModel):
    code: str
    message: str

class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None

# Auth
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    user_id: int

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# Case
class CaseCreate(BaseModel):
    case_number: str
    title: str
    institution_name: str
    review_date: Optional[datetime] = None

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    institution_name: Optional[str] = None
    status: Optional[str] = None
    review_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None

class CaseOut(BaseModel):
    id: int
    case_number: str
    title: str
    institution_name: str
    status: str
    review_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    document_count: Optional[int] = 0
    finding_count: Optional[int] = 0

    class Config:
        from_attributes = True

# Documents
class DocumentPageOut(BaseModel):
    page_number: int
    extracted_text: str
    ocr_engine: str
    mean_confidence: float
    layout_data: Optional[Any] = None
    has_image: bool = False

    class Config:
        from_attributes = True

class DocumentOut(BaseModel):
    id: int
    case_id: int
    doc_type: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    sha256_hash: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# Extracted Fields
class ExtractedFieldOut(BaseModel):
    id: int
    case_id: int
    document_id: int
    page_number: int
    field_key: str
    raw_value: str
    normalized_value: Optional[str] = None
    confidence: float
    bbox: Optional[dict[str, Any]] = None
    is_ambiguous: bool
    review_status: str
    extraction_method: str
    verbatim_snippet: Optional[str] = None
    document_name: Optional[str] = None

    class Config:
        from_attributes = True

class FieldCorrectionCreate(BaseModel):
    corrected_value: str
    reason: Optional[str] = None

# Analysis & Findings
class EvidenceItemOut(BaseModel):
    id: int
    source_label: str
    document_id: int
    page_number: int
    field_key: str
    raw_value: str
    normalized_value: Optional[str] = None
    bbox: Optional[dict[str, Any]] = None
    document_name: Optional[str] = None

    class Config:
        from_attributes = True

class FindingOut(BaseModel):
    id: int
    case_id: int
    analysis_run_id: Optional[int] = None
    rule_code: str
    rule_version: str
    severity: str
    title: str
    explanation: str
    uncertainty_note: Optional[str] = None
    system_status: str
    reviewer_status: str
    superseded: bool
    created_at: datetime
    evidence_items: list[EvidenceItemOut] = []

    class Config:
        from_attributes = True

class ReviewActionCreate(BaseModel):
    decision: str = Field(..., pattern="^(confirmed|dismissed|needs_more_evidence|resolved)$")
    comment: str = Field(..., min_length=3, description="Mandatory review comment for audit trail")

class AnalysisRunOut(BaseModel):
    id: int
    case_id: int
    input_hash: str
    rule_versions: dict[str, Any]
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None

    class Config:
        from_attributes = True

# Audit
class AuditEventOut(BaseModel):
    id: int
    case_id: int
    user_id: Optional[int] = None
    event_type: str
    payload: dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

# Rules
class ValidationRuleOut(BaseModel):
    id: int
    rule_code: str
    name: str
    description: str
    version: str
    is_active: bool
    severity: str
    parameters: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True

class ValidationRuleUpdate(BaseModel):
    is_active: Optional[bool] = None
    severity: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None

# Graph
class GraphNode(BaseModel):
    id: str
    type: str  # document | field | finding
    label: str
    data: dict[str, Any]

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None
    animated: Optional[bool] = False
    style: Optional[dict[str, Any]] = None

class CaseEvidenceGraphOut(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]

# Benchmarks
class BenchmarkRunOut(BaseModel):
    id: int
    total_cases: int
    precision: float
    recall: float
    f1_score: float
    tp_count: int
    fp_count: int
    fn_count: int
    duration_ms: int
    created_at: datetime
    case_results: list[dict[str, Any]] = []

    class Config:
        from_attributes = True

# Dashboard
class DashboardSummaryOut(BaseModel):
    total_cases: int
    total_documents: int
    findings_by_severity: dict[str, int]
    system_truth_states: dict[str, int]  # Consistent, Potential inconsistency, Needs human review
    recent_activity: list[dict[str, Any]]
    latest_benchmark: Optional[dict[str, Any]] = None

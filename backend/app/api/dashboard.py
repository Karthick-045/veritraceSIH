from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import ApplicationCase, Document, Finding, ExtractedField, AuditEvent, BenchmarkRun
from app.schemas.schemas import DashboardSummaryOut, ApiResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=ApiResponse[DashboardSummaryOut])
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_cases = db.query(ApplicationCase).count()
    total_docs = db.query(Document).count()

    active_findings = db.query(Finding).filter(Finding.superseded == False).all()

    by_severity = {"Info": 0, "Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    for f in active_findings:
        sev = f.severity if f.severity in by_severity else "Medium"
        by_severity[sev] += 1

    # Three-state truth counts
    # Needs human review: low confidence or ambiguous fields or findings with Info/needs_more_evidence
    needs_review_count = db.query(ExtractedField).filter(
        (ExtractedField.review_status == "needs_review") | (ExtractedField.is_ambiguous == True)
    ).count()

    potential_inconsistencies = len([f for f in active_findings if f.severity in ["Medium", "High", "Critical"]])
    consistent_checks = max(0, (total_docs * 4) - potential_inconsistencies - needs_review_count)

    truth_states = {
        "Consistent": consistent_checks,
        "Potential Inconsistency": potential_inconsistencies,
        "Needs Human Review": needs_review_count
    }

    # Recent activity
    audits = db.query(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(10).all()
    recent_activity = [{
        "id": a.id,
        "case_id": a.case_id,
        "event_type": a.event_type,
        "payload": a.payload,
        "created_at": a.created_at.isoformat()
    } for a in audits]

    # Latest benchmark
    latest_bench = db.query(BenchmarkRun).order_by(BenchmarkRun.created_at.desc()).first()
    bench_data = None
    if latest_bench:
        bench_data = {
            "id": latest_bench.id,
            "precision": latest_bench.precision,
            "recall": latest_bench.recall,
            "f1_score": latest_bench.f1_score,
            "total_cases": latest_bench.total_cases,
            "tp_count": latest_bench.tp_count,
            "fp_count": latest_bench.fp_count,
            "fn_count": latest_bench.fn_count
        }

    return ApiResponse(data=DashboardSummaryOut(
        total_cases=total_cases,
        total_documents=total_docs,
        findings_by_severity=by_severity,
        system_truth_states=truth_states,
        recent_activity=recent_activity,
        latest_benchmark=bench_data
    ))

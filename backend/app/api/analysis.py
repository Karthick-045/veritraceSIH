from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.rbac import get_current_user_optional
from app.models.models import AnalysisRun, User, Finding
from app.schemas.schemas import AnalysisRunOut, ApiResponse
from app.services.rule_engine import RuleEngine

router = APIRouter(tags=["Analysis"])

@router.post("/cases/{case_id}/analyze", response_model=ApiResponse[AnalysisRunOut])
def analyze_case(case_id: int, db: Session = Depends(get_db), current_user: User | None = Depends(get_current_user_optional)):
    try:
        run = RuleEngine.execute_analysis(db=db, case_id=case_id, user_id=current_user.id if current_user else None)
        return ApiResponse(data=AnalysisRunOut.model_validate(run))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/cases/{case_id}/runs", response_model=ApiResponse[list[AnalysisRunOut]])
def list_case_runs(case_id: int, db: Session = Depends(get_db)):
    runs = db.query(AnalysisRun).filter(AnalysisRun.case_id == case_id).order_by(AnalysisRun.started_at.desc()).all()
    return ApiResponse(data=[AnalysisRunOut.model_validate(r) for r in runs])

@router.post("/runs/{run_id}/reproduce", response_model=ApiResponse[dict])
def reproduce_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(AnalysisRun).filter(AnalysisRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Analysis run not found")

    # Capture original finding codes and counts
    orig_findings = db.query(Finding).filter(Finding.analysis_run_id == run.id).all()
    orig_signatures = sorted([f"{f.rule_code}:{f.title}:{f.severity}" for f in orig_findings])

    # Re-evaluate engine
    re_run = RuleEngine.execute_analysis(db=db, case_id=run.case_id)
    re_findings = db.query(Finding).filter(Finding.analysis_run_id == re_run.id).all()
    re_signatures = sorted([f"{f.rule_code}:{f.title}:{f.severity}" for f in re_findings])

    is_identical = (run.input_hash == re_run.input_hash) and (orig_signatures == re_signatures)

    return ApiResponse(data={
        "original_run_id": run.id,
        "new_run_id": re_run.id,
        "input_hash": run.input_hash,
        "identical": is_identical,
        "message": "Deterministic RuleEngine reproduced exact identical findings matching initial run." if is_identical else "Differences detected."
    })

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import BenchmarkRun, BenchmarkCaseResult
from app.schemas.schemas import BenchmarkRunOut, ApiResponse
from app.services.benchmark_service import BenchmarkService

router = APIRouter(prefix="/benchmarks", tags=["Benchmarks"])

@router.post("/run", response_model=ApiResponse[BenchmarkRunOut])
def trigger_benchmark(db: Session = Depends(get_db)):
    try:
        run = BenchmarkService.run_benchmark(db=db)
        case_res = db.query(BenchmarkCaseResult).filter(BenchmarkCaseResult.run_id == run.id).all()
        res_dicts = [{
            "case_key": cr.case_key,
            "expected_rules": cr.expected_rules,
            "detected_rules": cr.detected_rules,
            "tp": cr.tp,
            "fp": cr.fp,
            "fn": cr.fn,
            "duration_ms": cr.duration_ms
        } for cr in case_res]
        
        out = BenchmarkRunOut(
            id=run.id,
            total_cases=run.total_cases,
            precision=run.precision,
            recall=run.recall,
            f1_score=run.f1_score,
            tp_count=run.tp_count,
            fp_count=run.fp_count,
            fn_count=run.fn_count,
            duration_ms=run.duration_ms,
            created_at=run.created_at,
            case_results=res_dicts
        )
        return ApiResponse(data=out)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark execution failed: {str(e)}")

@router.get("", response_model=ApiResponse[list[BenchmarkRunOut]])
def list_benchmark_runs(db: Session = Depends(get_db)):
    runs = db.query(BenchmarkRun).order_by(BenchmarkRun.created_at.desc()).all()
    out = []
    for r in runs:
        out.append(BenchmarkRunOut(
            id=r.id,
            total_cases=r.total_cases,
            precision=r.precision,
            recall=r.recall,
            f1_score=r.f1_score,
            tp_count=r.tp_count,
            fp_count=r.fp_count,
            fn_count=r.fn_count,
            duration_ms=r.duration_ms,
            created_at=r.created_at,
            case_results=[]
        ))
    return ApiResponse(data=out)

@router.get("/{id}", response_model=ApiResponse[BenchmarkRunOut])
def get_benchmark_run(id: int, db: Session = Depends(get_db)):
    r = db.query(BenchmarkRun).filter(BenchmarkRun.id == id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Benchmark run not found")

    case_res = db.query(BenchmarkCaseResult).filter(BenchmarkCaseResult.run_id == r.id).all()
    res_dicts = [{
        "case_key": cr.case_key,
        "expected_rules": cr.expected_rules,
        "detected_rules": cr.detected_rules,
        "tp": cr.tp,
        "fp": cr.fp,
        "fn": cr.fn,
        "duration_ms": cr.duration_ms
    } for cr in case_res]

    out = BenchmarkRunOut(
        id=r.id,
        total_cases=r.total_cases,
        precision=r.precision,
        recall=r.recall,
        f1_score=r.f1_score,
        tp_count=r.tp_count,
        fp_count=r.fp_count,
        fn_count=r.fn_count,
        duration_ms=r.duration_ms,
        created_at=r.created_at,
        case_results=res_dicts
    )
    return ApiResponse(data=out)

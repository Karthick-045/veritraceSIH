import sys
from pathlib import Path
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.models import User, ValidationRule
from app.rules.registry import RULE_REGISTRY

from app.api.auth import router as auth_router
from app.api.cases import router as cases_router
from app.api.documents import router as documents_router
from app.api.analysis import router as analysis_router
from app.api.fields import router as fields_router
from app.api.findings import router as findings_router
from app.api.graph import router as graph_router
from app.api.audit import router as audit_router
from app.api.rules import router as rules_router
from app.api.benchmarks import router as benchmarks_router
from app.api.dashboard import router as dashboard_router
from app.api.simulation import router as simulation_router

# Initialize tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="VeriTrace: AI-Powered Application Validation Decision-Support Platform"
)

# CORS setup
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Error handlers adhering to blueprint specs: { "error": { "code", "message" } }
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "error": {"code": str(exc.status_code), "message": exc.detail}}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"data": None, "error": {"code": "422", "message": str(exc)}}
    )

# Routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(cases_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(analysis_router, prefix=settings.API_PREFIX)
app.include_router(fields_router, prefix=settings.API_PREFIX)
app.include_router(findings_router, prefix=settings.API_PREFIX)
app.include_router(graph_router, prefix=settings.API_PREFIX)
app.include_router(audit_router, prefix=settings.API_PREFIX)
app.include_router(rules_router, prefix=settings.API_PREFIX)
app.include_router(benchmarks_router, prefix=settings.API_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_PREFIX)
app.include_router(simulation_router, prefix=settings.API_PREFIX)

@app.on_event("startup")
def startup_seed():
    db = SessionLocal()
    try:
        # Seed users if none exist
        if not db.query(User).first():
            admin = User(
                email="admin@veritrace.gov.in",
                hashed_password=get_password_hash("admin123"),
                full_name="Chief Scrutiny Officer",
                role="admin"
            )
            reviewer = User(
                email="officer@veritrace.gov.in",
                hashed_password=get_password_hash("officer123"),
                full_name="Verification Reviewer",
                role="reviewer"
            )
            db.add_all([admin, reviewer])
            db.commit()

        # Seed rules if none exist
        if not db.query(ValidationRule).first():
            for r in RULE_REGISTRY.values():
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
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "VeriTrace", "version": settings.VERSION}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.rbac import require_admin
from app.models.models import ValidationRule, User
from app.schemas.schemas import ValidationRuleOut, ValidationRuleUpdate, ApiResponse
from app.rules.registry import RULE_REGISTRY

router = APIRouter(prefix="/rules", tags=["Validation Rules"])

@router.get("", response_model=ApiResponse[list[ValidationRuleOut]])
def list_rules(db: Session = Depends(get_db)):
    db_rules = db.query(ValidationRule).all()
    if not db_rules:
        # Seed from registry into DB if empty
        for r in RULE_REGISTRY.values():
            rule_obj = ValidationRule(
                rule_code=r.rule_code,
                name=r.name,
                description=r.description,
                version=r.version,
                is_active=True,
                severity=r.severity
            )
            db.add(rule_obj)
        db.commit()
        db_rules = db.query(ValidationRule).all()

    return ApiResponse(data=[ValidationRuleOut.model_validate(r) for r in db_rules])

@router.patch("/{id}", response_model=ApiResponse[ValidationRuleOut])
def update_rule(
    id: int,
    payload: ValidationRuleUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    rule = db.query(ValidationRule).filter(ValidationRule.id == id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    if payload.is_active is not None:
        rule.is_active = payload.is_active
    if payload.severity is not None:
        rule.severity = payload.severity
    if payload.parameters is not None:
        rule.parameters = payload.parameters

    db.commit()
    db.refresh(rule)
    return ApiResponse(data=ValidationRuleOut.model_validate(rule))

from sqlalchemy.orm import Session
from app.models.models import AuditEvent

class AuditService:
    @staticmethod
    def get_case_audit_trail(db: Session, case_id: int) -> list[AuditEvent]:
        return db.query(AuditEvent).filter(
            AuditEvent.case_id == case_id
        ).order_by(AuditEvent.created_at.asc()).all()

    @staticmethod
    def log_event(db: Session, case_id: int, event_type: str, payload: dict, user_id: int | None = None) -> AuditEvent:
        event = AuditEvent(
            case_id=case_id,
            user_id=user_id,
            event_type=event_type,
            payload=payload
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

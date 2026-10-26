from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.models import Finding, ReviewDecision, AuditEvent, ApplicationCase

class ReviewService:
    @staticmethod
    def submit_review(
        db: Session,
        finding_id: int,
        decision: str,  # confirmed | dismissed | needs_more_evidence | resolved
        comment: str,
        user_id: int
    ) -> Finding:
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if not finding:
            raise HTTPException(status_code=404, detail="Finding not found")

        if not comment or len(comment.strip()) < 3:
            raise HTTPException(status_code=400, detail="Review comment is mandatory (minimum 3 characters)")

        # Create ReviewDecision
        rev_decision = ReviewDecision(
            finding_id=finding.id,
            decision=decision,
            comment=comment.strip(),
            decided_by=user_id
        )
        db.add(rev_decision)

        # Update finding reviewer status (system_status is immutable!)
        old_status = finding.reviewer_status
        finding.reviewer_status = decision

        # Check if all findings for this case are reviewed
        remaining_pending = db.query(Finding).filter(
            Finding.case_id == finding.case_id,
            Finding.reviewer_status == "pending",
            Finding.superseded == False
        ).count()

        if remaining_pending == 0:
            case = db.query(ApplicationCase).filter(ApplicationCase.id == finding.case_id).first()
            if case:
                case.status = "reviewed"

        # Record Audit Event
        audit = AuditEvent(
            case_id=finding.case_id,
            user_id=user_id,
            event_type="FINDING_REVIEWED",
            payload={
                "finding_id": finding.id,
                "rule_code": finding.rule_code,
                "old_status": old_status,
                "new_decision": decision,
                "comment": comment.strip()
            }
        )
        db.add(audit)
        db.commit()
        db.refresh(finding)

        return finding

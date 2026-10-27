from datetime import datetime

from app.models.models import (
    AnalysisRun,
    ApplicationCase,
    AuditEvent,
    Document,
    ExtractedField,
    Finding,
)


def create_case_with_expiring_document(db_session):
    case = ApplicationCase(
        case_number="CASE-SIMULATION-01",
        title="Simulation test case",
        institution_name="Example Institute",
        review_date=datetime(2026, 6, 1),
    )
    db_session.add(case)
    db_session.flush()

    document = Document(
        case_id=case.id,
        doc_type="fire_safety",
        file_path="simulation-test.pdf",
        original_filename="simulation-test.pdf",
        mime_type="application/pdf",
        file_size_bytes=100,
        sha256_hash="a" * 64,
        status="extracted",
    )
    db_session.add(document)
    db_session.flush()

    field = ExtractedField(
        case_id=case.id,
        document_id=document.id,
        page_number=1,
        field_key="valid_until",
        raw_value="01/01/2025",
        normalized_value="2025-01-01",
        confidence=0.99,
        is_ambiguous=False,
        review_status="extracted",
        extraction_method="test",
    )
    db_session.add(field)
    db_session.commit()
    return case, document, field


def test_simulation_compares_review_date_and_does_not_persist(client, db_session):
    case, _, _ = create_case_with_expiring_document(db_session)
    before = (
        db_session.query(AnalysisRun).count(),
        db_session.query(Finding).count(),
        db_session.query(AuditEvent).count(),
    )

    unchanged_response = client.post(
        f"/api/cases/{case.id}/simulate",
        json={"review_date": "2026-06-01"},
    )
    assert unchanged_response.status_code == 200
    unchanged_result = unchanged_response.json()["data"]
    assert unchanged_result["scenario"]["finding_count"] == 1
    assert unchanged_result["added_findings"] == []
    assert unchanged_result["resolved_findings"] == []

    still_expired_response = client.post(
        f"/api/cases/{case.id}/simulate",
        json={"review_date": "2025-06-01"},
    )
    still_expired_result = still_expired_response.json()["data"]
    assert still_expired_result["scenario"]["finding_count"] == 1
    assert still_expired_result["added_findings"] == []
    assert still_expired_result["resolved_findings"] == []

    response = client.post(
        f"/api/cases/{case.id}/simulate",
        json={"review_date": "2024-06-01"},
    )

    assert response.status_code == 200
    result = response.json()["data"]
    assert result["baseline"]["finding_count"] == 1
    assert result["scenario"]["finding_count"] == 0
    assert len(result["resolved_findings"]) == 1

    after = (
        db_session.query(AnalysisRun).count(),
        db_session.query(Finding).count(),
        db_session.query(AuditEvent).count(),
    )
    assert after == before


def test_simulation_can_exclude_documents_and_override_dates(client, db_session):
    case, document, field = create_case_with_expiring_document(db_session)

    response = client.post(
        f"/api/cases/{case.id}/simulate",
        json={
            "field_overrides": [{"field_id": field.id, "raw_value": "2027-01-01"}],
        },
    )

    assert response.status_code == 200
    result = response.json()["data"]
    assert result["baseline"]["finding_count"] == 1
    assert result["scenario"]["included_document_count"] == 1
    assert result["scenario"]["finding_count"] == 0

    excluded_document_response = client.post(
        f"/api/cases/{case.id}/simulate",
        json={"excluded_document_ids": [document.id]},
    )
    assert excluded_document_response.status_code == 200
    assert excluded_document_response.json()["data"]["scenario"]["included_document_count"] == 0


def test_simulation_rejects_documents_from_another_case(client, db_session):
    case, document, _ = create_case_with_expiring_document(db_session)
    other_case = ApplicationCase(
        case_number="CASE-SIMULATION-02",
        title="Other simulation test case",
        institution_name="Other Institute",
    )
    db_session.add(other_case)
    db_session.commit()

    response = client.post(
        f"/api/cases/{other_case.id}/simulate",
        json={"excluded_document_ids": [document.id]},
    )

    assert response.status_code == 400

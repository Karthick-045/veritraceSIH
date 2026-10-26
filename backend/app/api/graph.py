from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Document, ExtractedField, Finding
from app.schemas.schemas import CaseEvidenceGraphOut, GraphNode, GraphEdge, ApiResponse

router = APIRouter(tags=["Graph"])

@router.get("/cases/{case_id}/graph", response_model=ApiResponse[CaseEvidenceGraphOut])
def get_case_evidence_graph(case_id: int, db: Session = Depends(get_db)):
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []

    docs = db.query(Document).filter(Document.case_id == case_id).all()
    fields = db.query(ExtractedField).filter(ExtractedField.case_id == case_id).all()
    findings = db.query(Finding).filter(Finding.case_id == case_id, Finding.superseded == False).all()

    # 1. Document nodes
    for d in docs:
        nodes.append(GraphNode(
            id=f"doc_{d.id}",
            type="documentNode",
            label=d.original_filename,
            data={
                "doc_id": d.id,
                "doc_type": d.doc_type,
                "status": d.status,
                "file_size": d.file_size_bytes
            }
        ))

    # 2. Field nodes & doc->field edges
    for f in fields:
        field_node_id = f"field_{f.id}"
        nodes.append(GraphNode(
            id=field_node_id,
            type="fieldNode",
            label=f"{f.field_key}: {f.raw_value[:20]}",
            data={
                "field_id": f.id,
                "field_key": f.field_key,
                "raw_value": f.raw_value,
                "normalized_value": f.normalized_value,
                "confidence": f.confidence,
                "is_ambiguous": f.is_ambiguous,
                "review_status": f.review_status
            }
        ))
        edges.append(GraphEdge(
            id=f"edge_doc_{f.document_id}_field_{f.id}",
            source=f"doc_{f.document_id}",
            target=field_node_id,
            label="extracts"
        ))

    # 3. Finding nodes & field->finding edges
    for find in findings:
        finding_node_id = f"finding_{find.id}"
        nodes.append(GraphNode(
            id=finding_node_id,
            type="findingNode",
            label=find.title,
            data={
                "finding_id": find.id,
                "rule_code": find.rule_code,
                "severity": find.severity,
                "reviewer_status": find.reviewer_status,
                "explanation": find.explanation
            }
        ))
        for ev in find.evidence_items:
            if ev.field_id:
                edges.append(GraphEdge(
                    id=f"edge_conflict_f{ev.field_id}_find{find.id}",
                    source=f"field_{ev.field_id}",
                    target=finding_node_id,
                    label="contradicts",
                    animated=True,
                    style={"stroke": "#ef4444", "strokeWidth": 2}
                ))
            else:
                edges.append(GraphEdge(
                    id=f"edge_conflict_doc{ev.document_id}_find{find.id}",
                    source=f"doc_{ev.document_id}",
                    target=finding_node_id,
                    label="flags",
                    animated=True,
                    style={"stroke": "#f59e0b", "strokeWidth": 2}
                ))

    return ApiResponse(data=CaseEvidenceGraphOut(nodes=nodes, edges=edges))

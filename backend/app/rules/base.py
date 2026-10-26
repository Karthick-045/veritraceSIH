from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel

class Claim:
    def __init__(
        self,
        field_id: int,
        doc_id: int,
        doc_name: str,
        doc_type: str,
        page_number: int,
        key: str,
        raw: str,
        normalized: str | None,
        confidence: float,
        bbox: dict[str, Any] | None,
        is_ambiguous: bool
    ):
        self.field_id = field_id
        self.doc_id = doc_id
        self.doc_name = doc_name
        self.doc_type = doc_type
        self.page_number = page_number
        self.key = key
        self.raw = raw
        self.normalized = normalized
        self.confidence = confidence
        self.bbox = bbox
        self.is_ambiguous = is_ambiguous

    @property
    def usable(self) -> bool:
        # Usable for deterministic contradiction checks if not low-confidence and not ambiguous
        return self.confidence >= 0.65 and not self.is_ambiguous and self.normalized is not None

    def as_evidence(self, source_label: str) -> dict[str, Any]:
        return {
            "source_label": source_label,
            "document_id": self.doc_id,
            "document_name": self.doc_name,
            "page_number": self.page_number,
            "field_id": self.field_id,
            "field_key": self.key,
            "raw_value": self.raw,
            "normalized_value": self.normalized,
            "bbox": self.bbox
        }

class EvaluatedFinding(BaseModel):
    rule_code: str
    rule_version: str
    severity: str
    title: str
    explanation: str
    uncertainty_note: str = "Potential inconsistency; reviewer confirmation is required."
    evidence: list[dict[str, Any]]

class Rule(ABC):
    rule_code: str
    name: str
    version: str
    description: str
    severity: str

    @abstractmethod
    def evaluate(self, claims: list[Claim], case_context: dict[str, Any]) -> list[EvaluatedFinding]:
        pass

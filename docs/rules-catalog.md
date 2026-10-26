# VeriTrace Deterministic Rule Catalog

All rules are versioned as code and record rule code, version, severity, and comparison evidence.

| Rule Code | Version | Severity | Trigger Condition | Non-Firing Conditions |
| :--- | :---: | :---: | :--- | :--- |
| `CROSS_DOC_VALUE_MISMATCH` | 1.0 | Medium (High for Inst. ID) | Normalized values of key fields differ between two documents with similarity < 85%. | Either value is low-confidence (<0.65) or missing. |
| `DATE_ORDER_INVALID` | 1.0 | High | Expiry / valid-until date is chronologically prior to issue date within the same document. | Either date is ambiguous or unparseable. |
| `EVIDENCE_EXPIRED` | 1.0 | Medium | Certificate valid-until date has elapsed prior to the case scrutiny review date. | Document type has no expiration requirement. |
| `ACADEMIC_YEAR_MISMATCH` | 1.0 | Medium | Academic year citations conflict between documents (e.g. `2024-25` vs `2025-26`). | Years normalize to the same canonical value (`2025-26` == `2025-2026`). |
| `LOW_CONFIDENCE_EXTRACTION` | 1.0 | Info | Extracted field confidence < 0.65 or date format is ambiguous (`03/04/2025`). | Value meets confidence threshold and format is unambiguous. |

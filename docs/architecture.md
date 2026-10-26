# VeriTrace Architecture & Technical Design

## 1. System Overview
```
┌──────────────────────────── React + Vite UI ────────────────────────────┐
│ Dashboard │ Cases │ Workspace │ Evidence Lens │ Review │ Graph │ Bench │
└───────────────────────────────┬──────────────────────────────────────────┘
                                │ REST / JSON (JWT)
┌───────────────────────────────▼──────────────────────────────────────────┐
│ FastAPI Application (Python 3.11+)                                       │
│ Auth / RBAC → routers: cases · documents · analysis · findings · bench   │
├──────────────────────────────────────────────────────────────────────────┤
│ Core Services:                                                           │
│  • DocumentService: Storage, validation, SHA256 checksumming             │
│  • ExtractionService: PyMuPDF + Tesseract fallback (word boxes + PNGs)   │
│  • FieldExtractor + NormalizationService: Anchored claims + bboxes       │
│  • RuleEngine: 5 versioned deterministic rules → EvidenceService         │
│  • ReviewService: Human decisions with mandatory comment audit           │
│  • BenchmarkService: Labelled evaluation, TP/FP/FN confusion tracking    │
├──────────────────────────────────────────────────────────────────────────┤
│ Storage Layer:                                                           │
│  • PostgreSQL 16 (Relational integrity) / SQLite zero-config fallback     │
│  • Local private storage (authenticated page rendering only)             │
└──────────────────────────────────────────────────────────────────────────┘
```

## 2. Data Flow Pipeline
1. **Case Registration**: Officer registers an institution application bundle.
2. **Ingestion & Integrity**: Documents are uploaded, SHA256 checksummed, and stored in a private directory.
3. **Extraction**: PyMuPDF extracts text, word-level coordinates (`x0, y0, x1, y1` normalized 0..1), and renders high-fidelity PNG pages.
4. **Anchor Extraction & Normalization**: Regex heuristics match critical fields. Quote-or-reject guard checks verbatim presence. Dates, academic years, and names are deterministically normalized. Ambiguous dates (e.g. `03/04/2025`) are flagged without guessing.
5. **Deterministic Rule Engine**: Enabled rules evaluate claims. Findings are linked to exact bounding boxes on both sides of a contradiction.
6. **Reproducibility Guarantee**: Each analysis run generates an input hash (`sha256(docs + claims + rule_versions)`). Re-running reproduces identical findings.
7. **Human Scrutiny**: Reviewer confirms or dismisses findings with mandatory reasoning. Original automated status is preserved immutably.

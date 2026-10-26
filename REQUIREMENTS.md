# VeriTrace Requirements & Specification (MVP Scope 60-70%)

## Problem Statement 26261 (SIH 2026)
**AI-Powered Application Validation Decision-Support System**

### Core Philosophy & Boundary Lines
1. **Decision Support, Not Fraud Detection**: The platform is an evidence-linked second pair of eyes for verification scrutiny officers. It never uses words like "fraud" or "fake" and never produces an automated verdict accusing an institution.
2. **Three-State Truth Model**:
   - `✔ Consistent`: Anchored claims agree across verified documents.
   - `⚠ Potential Inconsistency`: Claim values conflict or violate temporal constraints; highlighted with bounding boxes on both sides.
   - `❓ Needs Human Review`: OCR confidence < 0.65 or ambiguous date formatting (e.g. `03/04/2025` with no locale indicator).
3. **Deterministic Rules as Versioned Code**: The engine produces identical findings for identical document bundles (reproducible runs).
4. **Append-Only Audit Trail**: Every automated finding and human decision is preserved immutably with mandatory reviewer reasoning.

### Functional Matrix (P0 Scope)
- **F-01**: Seeded Authentication & RBAC (Admin vs Reviewer).
- **F-02**: Application Case CRUD with duplicate case number rejection (HTTP 409).
- **F-03**: Document Ingestion (PDF, PNG, JPG) with size/MIME verification and SHA256 checksums.
- **F-04**: Text & Layout Extraction (PyMuPDF with word-level bounding boxes, Tesseract fallback).
- **F-05**: Field Extraction & Deterministic Normalization (Institution Name, ID, Dates, Academic Years, Land Area).
- **F-06**: Versioned Rule Engine (5 core rules).
- **F-07**: Evidence Lens: Side-by-side synchronized document comparison with bounding box overlays.
- **F-08**: Human Review Decision Panel with mandatory comment tracking.
- **F-09**: Honest Benchmark Lab with TP/FP/FN confusion matrix and precision/recall reporting.
- **F-10**: Case Evidence Graph & Reproducibility Proof (`identical: true`).

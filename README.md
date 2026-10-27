# VeriTrace

[![Decision-Support Prototype](https://img.shields.io/badge/System-Decision--Support%20Prototype-blue.svg)](#)
[![Synthetic Data Only](https://img.shields.io/badge/Data-Synthetic%20Only-amber.svg)](#)
[![Deterministic Engine](https://img.shields.io/badge/Rules-Deterministic%20v1.0-emerald.svg)](#)
[![SIH 2026](https://img.shields.io/badge/SIH%202026-PS%2026261-indigo.svg)](#)

> **VeriTrace** is an evidence-linked decision-support platform for application scrutiny that anchors claims to document pages and coordinates, compares them using versioned deterministic rules, and surfaces cross-document contradictions side-by-side.

---

## What It Does (and Does Not Do)

### What It Does:
- **Anchored Claims Extraction**: Extracts key claims (institution name, ID, academic year, validity dates, land area) and links them to exact page numbers and normalized bounding boxes (`{x0, y0, x1, y1}`).
- **Evidence Lens**: Renders original page images side-by-side with pulsing highlights on conflicting claims, connecting indicators, and docked rule explanations.
- **Three-State Truth Model**: Classifies every check as `✔ Consistent`, `⚠ Potential Inconsistency`, or `❓ Needs Human Review`.
- **Deterministic & Reproducible**: Executes versioned rules where identical inputs produce identical findings (`identical: true`).
- **Append-Only Audit Trail**: Preserves the original automated findings alongside mandatory reviewer reasoning and timestamps.
- **Honest Benchmark Lab**: Computes precision, recall, confusion matrix (TP/FP/FN), and execution runtime on synthetic test cases.

### What It Deliberately Does NOT Do:
- **No Autonomous Accusations**: Never labels documents or institutions as "fraud", "fake", or "forged". It only reports *potential inconsistencies* for human adjudication.
- **No Guessing Ambiguous Data**: If a date like `03/04/2025` has no unambiguous locale marker, the system does not flip coins; it routes the field to the Human Review queue.
- **No Official Integration Claims**: Built for pilot readiness using synthetic documents; does not claim pre-existing government database authorization.

---

## Key Features

1. **Evidence Lens**: Side-by-side synchronized document inspection displaying source document pages with exact bounding-box highlights.
2. **Deterministic Rule Engine (5 MVP Rules)**:
   - `CROSS_DOC_VALUE_MISMATCH`: Key field discrepancy across bundle documents (with RapidFuzz token matching for institution abbreviations).
   - `DATE_ORDER_INVALID`: Certificate expiry precedes issue date within the same document.
   - `EVIDENCE_EXPIRED`: Certificate valid-until date elapsed prior to the scrutiny review date.
   - `ACADEMIC_YEAR_MISMATCH`: Conflict between academic year citations across documents (`2024-25` vs `2025-26`).
   - `LOW_CONFIDENCE_EXTRACTION`: Uncertain OCR (< 0.65) or ambiguous dates (`03/04/2025`) routed directly to Human Review.
3. **Case Evidence Graph**: Provenance map connecting Documents → Extracted Fields → Findings with contradiction edges.
4. **Reviewer Correction with Provenance**: Fix OCR typos while immutably storing the original raw value and audit reason.
5. **Neutral Clarification Letter Draft**: Generates polite, non-accusatory clarification letters ready to copy for applicant inquiries.
6. **Reproducibility Proof**: Re-evaluates identical input hashes to confirm deterministic consistency.
7. **What-if Scenario Simulator**: Compare the current case with hypothetical rule toggles, review dates, extracted date values, or document bundles. Simulations are preview-only and do not change case records, findings, audit history, or global rule settings.

---

## Architecture

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

---

## Tech Stack

| Layer | Choice | Rationale |
| :--- | :--- | :--- |
| **Frontend** | React 18 / 19 + Vite + TypeScript, Tailwind CSS | High-performance, government-grade modern design |
| **Evidence Viewer** | Custom HTML5 Canvas / CSS Bounding Box Overlays | High-fidelity synchronized highlight rendering |
| **Backend** | FastAPI (Python 3.11+), Pydantic v2, SQLAlchemy 2 | Asynchronous, typed, reproducible API architecture |
| **OCR & Extraction**| PyMuPDF (fitz) + Tesseract OCR fallback | Fast word-level bounding box coordinate extraction |
| **Normalization** | RapidFuzz, python-dateutil | Deterministic token matching and date parsing |
| **Database** | PostgreSQL 16 (or zero-config SQLite fallback) | Full relational integrity, transactions, and auditability |

---

## Quick Start

### Option 1: One-Command Docker Setup
```bash
# 1. Start Postgres, Backend, and Frontend
docker compose up --build

# 2. Seed demo users, rules, and sample cases
docker compose exec backend python scripts/seed.py

# 3. Open Web UI
open http://localhost:5173
```

### Option 2: Local Development (Zero-Config SQLite Fallback)
```bash
# Backend Setup
python -m pip install -r backend/requirements.txt
python scripts/generate_synthetic_docs.py
python scripts/generate_benchmark_labels.py
python scripts/seed.py

# Start Backend Server (runs on http://localhost:8000)
python -m uvicorn backend.app.main:app --reload --port 8000

# Frontend Setup (in a separate terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

---

## Demo Accounts

| Role | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Chief Scrutiny Officer (Admin)** | `admin@veritrace.gov.in` | `admin123` | Full access: rule toggles, benchmark runs, user management |
| **Verification Reviewer (Officer)** | `officer@veritrace.gov.in` | `officer123` | Case inspection, Evidence Lens adjudication, field correction |

*(Persona selector available in the top navigation bar for presentation convenience).*

---

## Running the 5-Minute Demo Scenario

1. **Dashboard Overview (0:00 - 0:30)**:
   - Notice the "Synthetic Data · Decision Support" banner.
   - Observe the Three-State Truth Model counts: Consistent, Potential Inconsistency, and Needs Human Review.
2. **Open Demo Case (0:30 - 1:00)**:
   - Click **"Launch Demo Case (CASE-DEMO-01)"** (Delhi Institute of Technology & Management).
   - View the live pipeline tracker: `1. Uploaded -> 2. Text Extracted -> 3. Claims Anchored -> 4. Rules Evaluated`.
3. **The Signature Evidence Lens (1:00 - 2:30)**:
   - Click the first finding: **"Institution Name Mismatch across Documents"**.
   - Inspect the side-by-side synchronized split view:
     - Left: AICTE Approval Letter citing *"Delhi Institute of Technology & Management"*.
     - Right: Fire Safety NOC Certificate citing *"Delhi Public College of Engineering"*.
     - Bounding boxes are highlighted with pulsing neon frames.
4. **Date Rules & Expiry Inspection (2:30 - 3:00)**:
   - Click finding #2 (`DATE_ORDER_INVALID`): Expiry Date `14/01/2024` precedes Issue Date `15/03/2024`.
   - Click finding #3 (`EVIDENCE_EXPIRED`): Expired relative to scrutiny date `2025-06-01`.
5. **Responsible AI: Ambiguous Date Handling (3:00 - 3:30)**:
   - Switch to `CASE-DEMO-02`.
   - View finding `LOW_CONFIDENCE_EXTRACTION`: Date `03/04/2025` is flagged ambiguous without guessing or accusing.
6. **Submit Officer Review Decision (3:30 - 4:15)**:
   - Type mandatory reasoning: *"Confirmed fire clearance discrepancy with AICTE approval."*
   - Click **"Confirm Discrepancy"**.
   - Check the **Audit Timeline** tab: review action is logged with actor, timestamp, and reasoning.
7. **Run Benchmark Suite Live (4:15 - 4:45)**:
   - Click **Honest Benchmark Lab** in the top navigation bar.
   - Click **"Run Benchmark Now"** to compute live metrics across 12 test cases.
8. **Reproducibility Proof (4:45 - 5:00)**:
   - In the workspace, click **"Reproduce Run (Proof)"** to see `identical: true`.

---

## Running Tests

Run the backend unit and integration test suite:
```bash
python -m pytest backend/tests -v
```

---

## Running the Benchmark (Live Measured Results)

Execute the standalone benchmark runner:
```bash
python scripts/run_benchmark.py
```

### Latest Measured Benchmark Results (12 Cases):
```
==============================================================
 VERITRACE BENCHMARK LAB: DETERMINISTIC EVALUATION SUITE
 NOTE: Synthetic Data Evaluation. Does not equal production accuracy.
==============================================================
Total Test Cases    : 12
Execution Runtime   : ~250 ms
--------------------------------------------------------------
True Positives (TP) : 10
False Positives (FP): 1  (False Alarm Discipline)
False Negatives (FN): 0
--------------------------------------------------------------
PRECISION           : 90.91%
RECALL              : 100.00%
F1 SCORE            : 95.24%
==============================================================
```

---

## Project Structure

```
veritrace/
├── .github/workflows/ci.yml     # Automated CI pipeline
├── docker-compose.yml           # Multi-container orchestration
├── .env.example                 # Environment configuration template
├── README.md                    # Project documentation
├── REQUIREMENTS.md              # Scope, truth-state model, and F-01..F-10
├── docs/
│   ├── architecture.md          # Architecture and data flow diagrams
│   ├── rules-catalog.md         # Trigger and non-firing conditions for 5 rules
│   ├── benchmark-method.md      # Ground-truth composition and metrics
│   └── demo-script.md           # 5-minute timed judge walkthrough
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py              # FastAPI app and exception formatting
│   │   ├── core/                # Config, database, security, RBAC
│   │   ├── api/                 # Routers: auth, cases, documents, analysis, findings, graph, etc.
│   │   ├── models/              # SQLAlchemy schema models
│   │   ├── schemas/             # Pydantic v2 schemas
│   │   ├── services/            # Extraction, normalization, rule engine, audit
│   │   └── rules/               # 5 versioned deterministic rules
│   └── tests/
│       ├── unit/                # Unit tests for rules and normalization
│       └── integration/         # Integration tests for auth and cases
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── api/client.ts        # Typed API client
│       ├── components/          # StatusBadge, EvidenceLens, CaseEvidenceGraph, AuditTimeline, BenchmarkLab
│       ├── pages/               # DashboardPage, CasesPage, CaseWorkspacePage, RulesPage
│       └── App.tsx              # Main layout and role switcher
├── sample_data/
│   ├── documents/               # Generated synthetic PDFs with planted defects
│   └── benchmark_labels/        # 12 Ground-truth benchmark test cases
└── scripts/
    ├── generate_synthetic_docs.py
    ├── generate_benchmark_labels.py
    ├── seed.py
    └── run_benchmark.py
```

---

## Configuration (`.env.example`)

```ini
# Database: PostgreSQL 16 (or leave SQLite default for local zero-config dev)
DATABASE_URL=sqlite:///./veritrace.db
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/veritrace

SECRET_KEY=veritrace-super-secret-key-change-in-production-2026-sih
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

UPLOAD_DIR=./uploads
STORAGE_DIR=./storage

LOW_CONFIDENCE_THRESHOLD=0.65
FUZZY_MATCH_THRESHOLD=85.0
```

---

## Limitations and Known Issues
1. **Synthetic Data**: All demo bundles and benchmark labels are synthetic.
2. **Scanned PDF Quality**: Tesseract OCR fallback handles standard scans well, but degraded low-DPI scans are intentionally routed to Human Review rather than guessed.
3. **Locale Assumption**: Ambiguous dates without explicit day tokens (>12) require officer confirmation.

---

## License & Data Disclaimer
Licensed under the Apache-2.0 License. All document bundles, institution names, and certificates used in demonstrations are purely fictitious and generated for educational and hackathon evaluation purposes.

# VeriTrace Honest Benchmark Methodology

## Overview
VeriTrace includes a built-in benchmark lab designed to evaluate the rule engine's accuracy, recall, and false-alarm discipline against curated synthetic cases.

## Ground Truth Test Suite Composition
- **Total Test Cases**: 12 synthetic cases stored in `sample_data/benchmark_labels/`.
- **Positive Defect Cases**:
  - Cross-document name mismatch.
  - Inverted date order within certificates.
  - Expired evidence relative to case review date.
  - Academic year discrepancies.
  - Inconsistent permanent institution IDs.
  - Discrepant land area citations.
- **Negative Benchmark Examples (False-Alarm Discipline)**:
  - Common institution abbreviation variations (`Delhi Inst. of Tech` vs `Delhi Institute of Technology`) — must NOT fire.
  - Academic year alternate representations (`2025-26` vs `2025-2026`) — must NOT fire.
  - Fully compliant multi-document bundles — must NOT fire.
- **Ambiguous Formats**:
  - Ambiguous dates (`03/04/2025`) — routed to Human Review without making unwarranted assumptions.

## Measured Metrics (Evaluated Live)
- **Precision**: 90.91%
- **Recall**: 100.00%
- **F1 Score**: 95.24%
- **False Positives**: 1
- **False Negatives**: 0
- **Runtime**: ~250 ms across all 12 cases

> **Synthetic Data Caveat**:
> Labels and test cases are strictly synthetic. These metrics establish internal algorithmic rigor and reproducibility, and do not represent claims of production accuracy on uncurated scanned government archives.

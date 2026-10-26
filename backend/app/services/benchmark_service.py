import os
import json
import time
from sqlalchemy.orm import Session
from app.models.models import BenchmarkRun, BenchmarkCaseResult
from app.rules.base import Claim
from app.rules.registry import RULE_REGISTRY

class BenchmarkService:
    @staticmethod
    def run_benchmark(db: Session, labels_dir: str = "sample_data/benchmark_labels") -> BenchmarkRun:
        start_time = time.time()
        
        # Load benchmark definitions
        case_files = []
        if os.path.exists(labels_dir):
            for fname in sorted(os.listdir(labels_dir)):
                if fname.endswith(".json"):
                    case_files.append(os.path.join(labels_dir, fname))

        total_tp = 0
        total_fp = 0
        total_fn = 0
        case_results = []

        for c_file in case_files:
            c_start = time.time()
            with open(c_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            case_key = data.get("case_key", os.path.basename(c_file))
            expected_rules = set(data.get("expected_rules", []))
            claims_data = data.get("claims", [])
            case_context = data.get("case_context", {})

            # Convert claims
            claims: list[Claim] = []
            for idx, cd in enumerate(claims_data):
                claims.append(Claim(
                    field_id=idx + 1,
                    doc_id=cd.get("doc_id", 1),
                    doc_name=cd.get("doc_name", f"Doc {cd.get('doc_id', 1)}"),
                    doc_type=cd.get("doc_type", "general"),
                    page_number=cd.get("page_number", 1),
                    key=cd.get("key", ""),
                    raw=cd.get("raw", ""),
                    normalized=cd.get("normalized", cd.get("raw", "")),
                    confidence=cd.get("confidence", 1.0),
                    bbox=cd.get("bbox", {"x0": 0.1, "y0": 0.2, "x1": 0.5, "y1": 0.3}),
                    is_ambiguous=cd.get("is_ambiguous", False)
                ))

            detected_rules = set()
            for rule_code, rule_instance in RULE_REGISTRY.items():
                findings = rule_instance.evaluate(claims, case_context)
                if findings:
                    detected_rules.add(rule_code)

            tp = len(expected_rules.intersection(detected_rules))
            fp = len(detected_rules.difference(expected_rules))
            fn = len(expected_rules.difference(detected_rules))

            total_tp += tp
            total_fp += fp
            total_fn += fn

            c_dur = int((time.time() - c_start) * 1000)
            case_results.append({
                "case_key": case_key,
                "expected_rules": list(expected_rules),
                "detected_rules": list(detected_rules),
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "duration_ms": c_dur
            })

        precision = round(total_tp / (total_tp + total_fp), 4) if (total_tp + total_fp) > 0 else 1.0
        recall = round(total_tp / (total_tp + total_fn), 4) if (total_tp + total_fn) > 0 else 1.0
        f1 = round(2 * (precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 1.0
        duration_ms = int((time.time() - start_time) * 1000)

        # Store run
        bench_run = BenchmarkRun(
            total_cases=len(case_results),
            precision=precision,
            recall=recall,
            f1_score=f1,
            tp_count=total_tp,
            fp_count=total_fp,
            fn_count=total_fn,
            duration_ms=duration_ms
        )
        db.add(bench_run)
        db.commit()
        db.refresh(bench_run)

        for cr in case_results:
            b_case = BenchmarkCaseResult(
                run_id=bench_run.id,
                case_key=cr["case_key"],
                expected_rules=cr["expected_rules"],
                detected_rules=cr["detected_rules"],
                tp=cr["tp"],
                fp=cr["fp"],
                fn=cr["fn"],
                duration_ms=cr["duration_ms"]
            )
            db.add(b_case)

        db.commit()
        return bench_run

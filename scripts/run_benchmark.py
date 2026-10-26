import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))

from app.core.database import SessionLocal
from app.services.benchmark_service import BenchmarkService

def main():
    print("==============================================================")
    print(" VERITRACE BENCHMARK LAB: DETERMINISTIC EVALUATION SUITE")
    print(" NOTE: Synthetic Data Evaluation. Does not equal production accuracy.")
    print("==============================================================")
    db = SessionLocal()
    try:
        run = BenchmarkService.run_benchmark(db)
        print(f"\nBenchmark Run ID    : {run.id}")
        print(f"Total Test Cases    : {run.total_cases}")
        print(f"Execution Runtime   : {run.duration_ms} ms")
        print("--------------------------------------------------------------")
        print(f"True Positives (TP) : {run.tp_count}")
        print(f"False Positives (FP): {run.fp_count}  (False Alarm Discipline)")
        print(f"False Negatives (FN): {run.fn_count}")
        print("--------------------------------------------------------------")
        print(f"PRECISION           : {run.precision * 100:.2f}%")
        print(f"RECALL              : {run.recall * 100:.2f}%")
        print(f"F1 SCORE            : {run.f1_score * 100:.2f}%")
        print("==============================================================")
    finally:
        db.close()

if __name__ == "__main__":
    main()

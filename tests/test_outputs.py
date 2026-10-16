"""Lightweight reproducibility and QA assertions."""

from pathlib import Path
import json

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ed = pd.read_csv(ROOT / "data/processed/ed_analytic.csv", dtype={"facility_id": str})
qa = pd.read_csv(ROOT / "outputs/tables/qa_checks.csv")
results = json.loads((ROOT / "outputs/tables/key_results.json").read_text())

assert ed.facility_id.is_unique, "analytic mart must be one row per facility"
assert ed.facility_id.str.len().eq(6).all(), "CMS facility IDs must retain leading zeros"
assert ed.all_patient_ed_minutes.dropna().between(1, 3000).all()
assert ed.left_before_seen_pct.dropna().between(0, 100).all()
assert int(qa.loc[qa.check_name == "duplicate_facility_measure", "result"].iloc[0]) == 0
assert int(qa.loc[qa.check_name == "missing_hospital_join", "result"].iloc[0]) == 0
assert results["op18a_reporting_hospitals"] > 3000
assert (ROOT / "outputs/figures/cms_ed_throughput_dashboard.png").stat().st_size > 100_000
print("All output and QA assertions passed.")


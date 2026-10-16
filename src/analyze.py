"""Build the ED throughput analysis, validation tables, and dashboard."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


VOLUME_ORDER = ["low", "medium", "high", "very high"]
VOLUME_LABELS = {
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "very high": "Very high",
}


def bootstrap_median_ci(values: pd.Series, seed: int = 20261016, reps: int = 5000) -> tuple[float, float]:
    x = values.dropna().to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    boot = np.median(rng.choice(x, size=(reps, len(x)), replace=True), axis=1)
    return tuple(np.quantile(boot, [0.025, 0.975]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--table-dir", type=Path, default=Path("outputs/tables"))
    parser.add_argument("--figure-dir", type=Path, default=Path("outputs/figures"))
    args = parser.parse_args()
    for directory in (args.processed_dir, args.table_dir, args.figure_dir):
        directory.mkdir(parents=True, exist_ok=True)

    manifest = json.loads((args.raw_dir / "manifest.json").read_text(encoding="utf-8"))
    date_stamp = manifest["retrieved_utc_date"]
    ed_path = args.raw_dir / f"cms_ed_measures_{date_stamp}.csv"
    hospital_path = args.raw_dir / f"cms_hospital_general_information_{date_stamp}.csv"
    national_path = args.raw_dir / f"cms_ed_national_{date_stamp}.csv"

    con = duckdb.connect()
    sql = Path("sql/build_analytic_dataset.sql").read_text(encoding="utf-8")
    con.execute("SET VARIABLE ed_file = ?", [str(ed_path)])
    con.execute("SET VARIABLE hospital_file = ?", [str(hospital_path)])
    # DuckDB parameter variables in COPY/read_csv are substituted explicitly.
    sql = sql.replace("$ed_file", f"getvariable('ed_file')")
    sql = sql.replace("$hospital_file", f"getvariable('hospital_file')")
    con.execute(sql)
    con.execute(
        "COPY ed_analytic TO ? (HEADER, DELIMITER ',')",
        [str(args.processed_dir / "ed_analytic.csv")],
    )
    con.execute(
        "COPY qa_checks TO ? (HEADER, DELIMITER ',')",
        [str(args.table_dir / "qa_checks.csv")],
    )
    ed = con.table("ed_analytic").df()

    eligible = ed.dropna(subset=["all_patient_ed_minutes"]).copy()
    national = pd.read_csv(national_path)
    cms_national_op18a = float(
        national.loc[national.measure_id == "OP_18a", "score"].iloc[0]
    )
    overall_median = float(eligible["all_patient_ed_minutes"].median())
    q25, q75 = eligible["all_patient_ed_minutes"].quantile([0.25, 0.75])
    ci_low, ci_high = bootstrap_median_ci(eligible["all_patient_ed_minutes"])

    by_volume = (
        eligible[eligible["ed_volume"].isin(VOLUME_ORDER)]
        .groupby("ed_volume", observed=True)["all_patient_ed_minutes"]
        .agg(hospitals="size", median_minutes="median", q25=lambda x: x.quantile(.25), q75=lambda x: x.quantile(.75))
        .reindex(VOLUME_ORDER)
        .reset_index()
    )
    by_volume.to_csv(args.table_dir / "ed_time_by_volume.csv", index=False)

    state_summary = (
        eligible.groupby("state")["all_patient_ed_minutes"]
        .agg(hospitals_reporting="size", median_minutes="median", q25=lambda x: x.quantile(.25), q75=lambda x: x.quantile(.75))
        .reset_index()
    )
    state_summary["hours_median"] = state_summary["median_minutes"] / 60
    state_summary.sort_values("median_minutes", ascending=False).to_csv(
        args.table_dir / "state_benchmarks.csv", index=False
    )

    ownership = (
        eligible.groupby("hospital_ownership")["all_patient_ed_minutes"]
        .agg(hospitals="size", median_minutes="median", q25=lambda x: x.quantile(.25), q75=lambda x: x.quantile(.75))
        .reset_index()
        .sort_values("hospitals", ascending=False)
    )
    ownership.to_csv(args.table_dir / "ed_time_by_ownership.csv", index=False)

    reporting = pd.DataFrame(
        {
            "measure": ["All patients (OP_18a)", "Treat-and-release (OP_18b)", "Psychiatric patients (OP_18c)", "Transfers (OP_18d)", "Left before seen (OP_22)"],
            "hospitals_reporting": [
                ed[c].notna().sum() for c in ["all_patient_ed_minutes", "treat_release_ed_minutes", "psychiatric_ed_minutes", "transfer_ed_minutes", "left_before_seen_pct"]
            ],
        }
    )
    reporting["reporting_pct_of_ed_facilities"] = 100 * reporting["hospitals_reporting"] / len(ed)
    reporting.to_csv(args.table_dir / "measure_reporting_completeness.csv", index=False)

    groups = [
        eligible.loc[eligible.ed_volume == level, "all_patient_ed_minutes"].dropna().to_numpy()
        for level in VOLUME_ORDER
    ]
    groups = [x for x in groups if len(x) > 0]
    kw = stats.kruskal(*groups)

    priority = eligible[
        (eligible["all_patient_ed_minutes"] >= q75)
        & (eligible["all_patient_ed_minutes"] >= overall_median + 60)
    ].copy()
    priority["minutes_above_hospital_median"] = priority["all_patient_ed_minutes"] - overall_median
    priority.sort_values(["all_patient_ed_minutes", "facility_id"], ascending=[False, True]).to_csv(
        args.table_dir / "benchmark_review_list.csv", index=False
    )

    results = {
        "retrieved_date": date_stamp,
        "facilities_in_mart": int(len(ed)),
        "op18a_reporting_hospitals": int(len(eligible)),
        "op18a_reporting_pct": round(100 * len(eligible) / len(ed), 1),
        "hospital_median_minutes": round(overall_median, 1),
        "cms_national_op18a_minutes": round(cms_national_op18a, 1),
        "hospital_median_95ci": [round(ci_low, 1), round(ci_high, 1)],
        "hospital_iqr_minutes": [round(float(q25), 1), round(float(q75), 1)],
        "priority_review_hospitals": int(len(priority)),
        "psychiatric_reporting_hospitals": int(ed.psychiatric_ed_minutes.notna().sum()),
        "psychiatric_reporting_pct": round(100 * ed.psychiatric_ed_minutes.notna().sum() / len(ed), 1),
        "kruskal_volume_statistic": round(float(kw.statistic), 3),
        "kruskal_volume_pvalue": float(kw.pvalue),
    }
    (args.table_dir / "key_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    plt.style.use("default")
    fig = plt.figure(figsize=(15, 9), facecolor="#f5f7fa")
    gs = fig.add_gridspec(2, 3, height_ratios=[0.8, 2.4], hspace=0.38, wspace=0.35)
    ax_title = fig.add_subplot(gs[0, :])
    ax_title.axis("off")
    ax_title.text(0, .95, "U.S. emergency department throughput", fontsize=23, weight="bold", color="#143642", va="top")
    ax_title.text(0, .63, "Hospital-reported medians | CMS Care Compare | measurement period ending 2025-09-30", fontsize=11, color="#52636b")
    ax_title.text(0, .25, f"{overall_median:.0f} min", fontsize=32, weight="bold", color="#006d77")
    ax_title.text(.22, .31, f"median across {len(eligible):,} reporting hospitals\n95% bootstrap CI {ci_low:.0f}–{ci_high:.0f}; CMS national score {cms_national_op18a:.0f}", fontsize=11, color="#334e58", va="center")
    ax_title.text(.55, .25, f"{reporting.loc[2, 'reporting_pct_of_ed_facilities']:.1f}%", fontsize=32, weight="bold", color="#e76f51")
    ax_title.text(.78, .31, "of ED facilities reported the\npsychiatric-patient measure", fontsize=11, color="#334e58", va="center")

    ax1 = fig.add_subplot(gs[1, 0])
    plot_volume = by_volume.dropna(subset=["median_minutes"])
    ax1.barh([VOLUME_LABELS[x] for x in plot_volume.ed_volume], plot_volume.median_minutes, color=["#83c5be", "#55a6a0", "#278b88", "#006d77"])
    for i, v in enumerate(plot_volume.median_minutes):
        ax1.text(v + 3, i, f"{v:.0f}", va="center", fontsize=10)
    ax1.set_title("Median ED time by volume", loc="left", weight="bold")
    ax1.set_xlabel("Minutes; lower is better")
    ax1.spines[["top", "right", "left"]].set_visible(False)
    ax1.grid(axis="x", color="#dce4e7", linewidth=.8)
    ax1.set_axisbelow(True)

    ax2 = fig.add_subplot(gs[1, 1])
    top_states = state_summary.query("hospitals_reporting >= 20").nlargest(10, "median_minutes").sort_values("median_minutes")
    ax2.barh(top_states.state, top_states.median_minutes, color="#e9c46a")
    for i, v in enumerate(top_states.median_minutes):
        ax2.text(v + 3, i, f"{v:.0f}", va="center", fontsize=9)
    ax2.axvline(overall_median, color="#006d77", linestyle="--", linewidth=1.5, label="U.S. hospital median")
    ax2.set_title("Highest state medians", loc="left", weight="bold")
    ax2.set_xlabel("Minutes; states with ≥20 hospitals")
    ax2.spines[["top", "right", "left"]].set_visible(False)
    ax2.grid(axis="x", color="#dce4e7", linewidth=.8)
    ax2.set_axisbelow(True)
    ax2.legend(frameon=False, fontsize=8, loc="upper left")

    ax3 = fig.add_subplot(gs[1, 2])
    rep = reporting.sort_values("reporting_pct_of_ed_facilities")
    ax3.barh(rep.measure.str.replace(r" \(OP_.*\)", "", regex=True), rep.reporting_pct_of_ed_facilities, color="#8ecae6")
    for i, v in enumerate(rep.reporting_pct_of_ed_facilities):
        ax3.text(v + 1, i, f"{v:.1f}%", va="center", fontsize=9)
    ax3.set_xlim(0, 108)
    ax3.set_title("Measure availability", loc="left", weight="bold")
    ax3.set_xlabel("Percent of facilities in analytic mart")
    ax3.spines[["top", "right", "left"]].set_visible(False)
    ax3.grid(axis="x", color="#dce4e7", linewidth=.8)
    ax3.set_axisbelow(True)

    fig.text(.01, .01, "Interpretation: descriptive benchmarking—not a hospital ranking or causal analysis. State values are medians of hospital medians and are not patient-weighted.", fontsize=9, color="#52636b")
    fig.savefig(args.figure_dir / "cms_ed_throughput_dashboard.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()


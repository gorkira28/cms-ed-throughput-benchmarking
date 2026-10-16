# Portfolio case study: CMS ED Throughput Benchmarking

## The problem

Public ED time measures can support operational benchmarking, but naïve rankings hide differences in volume, reporting completeness, and aggregation. I built a reproducible workflow to turn the July 2026 CMS Care Compare release into a transparent hospital-level benchmark.

## What I built

I used Python to acquire and validate the CMS extracts, DuckDB SQL to create a one-row-per-facility analytic mart, and Python for bootstrap inference, nonparametric comparison, QA, and visualization. The repository also includes Tableau/Power BI-ready CSVs, automated tests, a checksum manifest, and a documented review-list rule.

## What the analysis found

Among 4,052 hospitals with OP-18a data, the median hospital reported 154 minutes from ED arrival to departure. The official CMS national score was 168 minutes, illustrating why an unweighted median of hospitals must not be presented as the national patient experience. Median time rose from 128 minutes in low-volume EDs to 197 minutes in very-high-volume EDs. Only 64.9% of facilities reported a usable psychiatric-patient ED time.

## Why it matters

The project shows how an analyst can move beyond a leaderboard: define the cohort, preserve suppressed values, distinguish aggregation methods, quantify missingness, test peer-group differences, and state what the data cannot prove. The output is a starting point for hospital operations review—not a causal or patient-level assessment.

**Tools:** Python, DuckDB SQL, CMS open data, bootstrap confidence intervals, Kruskal–Wallis testing, data visualization, QA/QC.


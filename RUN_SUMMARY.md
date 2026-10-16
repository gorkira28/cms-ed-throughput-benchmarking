# Friday portfolio run — October 16, 2026

## Review status

**Ready for Kira's review. Nothing has been published or pushed.**

Project: **CMS Emergency Department Throughput Benchmarking**  
Tools: **Python + DuckDB SQL + CMS open data**  
Target roles: healthcare data analyst, clinical data analyst, epidemiologist, biostatistician

## Key findings

1. The analytic mart contains 4,658 facilities; 4,052 (87.0%) reported numeric OP-18a values.
2. The median across hospital-reported medians was 154 minutes (bootstrap 95% CI: 152–156; IQR: 125–194.25).
3. CMS separately published a 168-minute national OP-18a score. The project explicitly prevents these differently aggregated statistics from being conflated.
4. Median hospital values increased from 128 minutes in low-volume EDs to 197 minutes in very-high-volume EDs.
5. Psychiatric-patient ED time was available for 64.9% of facilities; transfer time was available for 50.8%.
6. Among states with at least 20 reporting hospitals, Maryland had the highest median (249 minutes), followed by Massachusetts (225.5) and New York (210).
7. The transparent review rule identified 640 facilities for deeper operational review. This is a screening list, not a performance grade.

## Validation performed

- Reproduced the analysis from the downloaded CMS files.
- Passed all automated assertions in `tests/test_outputs.py`.
- Confirmed 27,948 unique facility-measure records and zero duplicates.
- Confirmed 4,658 analytic rows and zero failed joins to hospital information.
- Confirmed zero negative time values and zero percentages outside 0–100.
- Generated raw-file SHA-256 checksums and row counts in `data/raw/manifest.json`.
- Python source compiled successfully.
- DuckDB SQL executed successfully from end to end.
- Dashboard visually inspected after regeneration.
- Checked all internal Markdown links and official external references. CMS/GitHub links resolved; LinkedIn returned its expected anti-automation status during automated checking.
- GitHub profile audit confirmed professional name, bio, website, `hireable` status, six public repositories, consistent recent repository descriptions, and appropriate topic coverage.

## Files created in the project

- `README.md`
- `CITATION.cff`
- `LICENSE`
- `requirements.txt`
- `run_pipeline.ps1`
- `src/acquire_data.py`
- `src/analyze.py`
- `sql/build_analytic_dataset.sql`
- `tests/test_outputs.py`
- `docs/data_dictionary.md`
- `docs/methodology.md`
- `docs/references.md`
- `data/raw/cms_ed_measures_2026-10-16.csv`
- `data/raw/cms_ed_national_2026-10-16.csv`
- `data/raw/cms_hospital_general_information_2026-10-16.csv`
- `data/raw/manifest.json`
- `data/processed/ed_analytic.csv`
- `outputs/figures/cms_ed_throughput_dashboard.png`
- `outputs/tables/benchmark_review_list.csv`
- `outputs/tables/ed_time_by_ownership.csv`
- `outputs/tables/ed_time_by_volume.csv`
- `outputs/tables/key_results.json`
- `outputs/tables/measure_reporting_completeness.csv`
- `outputs/tables/qa_checks.csv`
- `outputs/tables/state_benchmarks.csv`
- `PORTFOLIO_CASE_STUDY.md`
- `LINKEDIN_POST_DRAFT.md`
- `REVIEW_CHECKLIST.md`
- `RUN_SUMMARY.md`

## Prepared profile and website changes

- Modified `publish-profile/README.md` locally to add the project as a clearly labeled review-stage item.
- Modified `publish-site/index.html` locally to add the portfolio case-study card.
- Added `publish-site/assets/cms_ed_throughput_dashboard.png` locally.
- None of these prepared changes have been pushed or deployed.

## Unresolved limitations

- Public hospital medians conceal patient-level variation.
- The analysis cannot adjust for acuity, staffing, boarding, capacity, referral patterns, or arrival time.
- Psychiatric and transfer measures have substantial missingness that may not be random.
- State results are unweighted medians of reporting hospitals and can reflect hospital mix.
- The Kruskal–Wallis result is unadjusted and does not establish that volume causes longer ED time.
- The 640-facility review list requires local context before any operational conclusion.

## Proposed GitHub metadata

- **Repository:** `cms-ed-throughput-benchmarking`
- **Description:** `CMS Care Compare analysis of U.S. emergency-department throughput, volume patterns, and reporting gaps using Python and DuckDB SQL.`
- **Homepage:** `https://gorkira28.github.io/#work`
- **Topics:** `healthcare-analytics`, `emergency-department`, `cms`, `hospital-quality`, `duckdb`, `sql`, `python`, `data-quality`, `data-visualization`, `reproducible-research`
- **Pin recommendation after publication:** add this project as the first pin, followed by the clinical-trial, pertussis, NHANES, Texas atlas, and portfolio-site repositories.

## Approval requested

Please approve or request edits for:

- [ ] GitHub repository creation and push
- [ ] GitHub metadata and topics
- [ ] GitHub profile README update
- [ ] Portfolio website case-study update and deployment
- [ ] LinkedIn post text
- [ ] LinkedIn dashboard image and first-comment repository link


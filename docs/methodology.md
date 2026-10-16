# Methodology

## Study design

Cross-sectional, facility-level descriptive analysis of the July 2026 CMS Care Compare hospital release. The main measurement period for OP-18a through OP-18d is October 1, 2024 through September 30, 2025. OP-22 and ED-volume reporting periods differ and are retained exactly as published.

## Cohort

The analytic mart begins with every facility appearing in at least one selected CMS ED measure: EDV, OP-18a, OP-18b, OP-18c, OP-18d, or OP-22. The primary cohort includes facilities with a numeric OP-18a value. Values such as `Not Available` are converted to missing and are not imputed.

## Measures

- **OP-18a:** median time all patients spent in the ED before leaving, including psychiatric/mental-health patients and patients transferred elsewhere.
- **OP-18b:** median ED time excluding psychiatric/mental-health patients and transfers.
- **OP-18c:** median ED time among psychiatric/mental-health patients.
- **OP-18d:** median ED time among patients transferred to another facility.
- **OP-22:** percentage leaving before being seen.
- **EDV:** CMS categorical ED volume: low, medium, high, or very high.

## Processing

1. Resolve official CSV download URLs from CMS dataset metadata.
2. Download hospital, national, and ED measure files.
3. Keep six ED measures and create a checksum manifest.
4. Parse numeric values without altering suppressed/unavailable records.
5. Pivot to one row per CMS facility ID.
6. Join hospital type, ownership, emergency-service indicator, and overall rating.
7. Run SQL data-quality checks and export an analysis-ready table.

## Statistical analysis

- Report median and interquartile range across reporting hospitals.
- Generate a percentile bootstrap 95% confidence interval for the hospital-level median using 5,000 resamples and a fixed seed (`20261016`).
- Summarize ED time by CMS volume category, ownership, and state.
- Use a Kruskal–Wallis test to assess whether OP-18a distributions differ across volume categories. The test does not identify cause and should not be treated as adjusted evidence.
- Restrict the displayed state chart to states/territories with at least 20 reporting hospitals to reduce instability. The full state table retains every geography.
- Create a transparent review list for facilities meeting both criteria: OP-18a at or above the 75th percentile and at least 60 minutes above the hospital-level median.

## Why 154 and 168 minutes both appear

The 154-minute estimate is the unweighted median of hospital-reported medians calculated in this project. The 168-minute value is the separately published CMS national OP-18a score. Aggregation methods and weighting differ, so the two values answer different questions and should not be expected to match.

## Limitations

1. Hospital medians conceal within-hospital variation and patient-level disparities.
2. Public values do not support adjustment for acuity, staffing, boarding, arrival time, or local capacity.
3. ED volume is categorical; exact annual visit counts are not published in this extract.
4. Group differences are unadjusted and can reflect hospital mix and geography.
5. Missingness is substantial for psychiatric and transfer measures and may be informative rather than random.
6. State summaries are medians of available hospital values, not patient-weighted state estimates.
7. Public reporting periods vary across selected measures.
8. The review list is a screening artifact, not a quality grade.

## Ethics and privacy

The project uses public facility-level data only. It contains no protected health information or individual records. Results should be used to generate questions and inform equitable operational review, not to stigmatize hospitals, communities, or patients seeking psychiatric care.


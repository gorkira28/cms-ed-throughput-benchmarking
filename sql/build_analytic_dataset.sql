-- CMS emergency department throughput analytic mart.
-- Scores are hospital-reported medians. State/national summaries below are
-- medians across hospitals and are not patient-weighted estimates.

CREATE OR REPLACE TABLE ed_long AS
SELECT
    trim(facility_id) AS facility_id,
    facility_name,
    city_town AS city,
    state,
    county_parish AS county,
    measure_id,
    measure_name,
    CASE WHEN regexp_matches(score, '^[0-9]+(\\.[0-9]+)?$')
         THEN CAST(score AS DOUBLE) END AS score_numeric,
    CASE WHEN regexp_matches(sample, '^[0-9]+(\\.[0-9]+)?$')
         THEN CAST(sample AS DOUBLE) END AS sample_numeric,
    nullif(footnote, '') AS footnote,
    strptime(start_date, '%m/%d/%Y')::DATE AS start_date,
    strptime(end_date, '%m/%d/%Y')::DATE AS end_date
FROM read_csv_auto($ed_file, all_varchar=true);

CREATE OR REPLACE TABLE hospital_info AS
SELECT
    trim(facility_id) AS facility_id,
    facility_name,
    state,
    hospital_type,
    hospital_ownership,
    emergency_services,
    CASE WHEN regexp_matches(hospital_overall_rating, '^[1-5]$')
         THEN CAST(hospital_overall_rating AS INTEGER) END AS overall_rating
FROM read_csv_auto($hospital_file, all_varchar=true);

CREATE OR REPLACE TABLE ed_wide AS
PIVOT (
    SELECT facility_id, measure_id, score_numeric
    FROM ed_long
) ON measure_id USING max(score_numeric);

CREATE OR REPLACE TABLE ed_volume AS
SELECT facility_id, lower(score) AS ed_volume
FROM read_csv_auto($ed_file, all_varchar=true)
WHERE measure_id = 'EDV';

CREATE OR REPLACE TABLE ed_analytic AS
SELECT
    w.facility_id,
    h.facility_name,
    h.state,
    h.hospital_type,
    h.hospital_ownership,
    h.emergency_services,
    h.overall_rating,
    v.ed_volume,
    w.OP_18a AS all_patient_ed_minutes,
    w.OP_18b AS treat_release_ed_minutes,
    w.OP_18c AS psychiatric_ed_minutes,
    w.OP_18d AS transfer_ed_minutes,
    w.OP_22 AS left_before_seen_pct
FROM ed_wide w
LEFT JOIN hospital_info h USING (facility_id)
LEFT JOIN ed_volume v USING (facility_id);

CREATE OR REPLACE TABLE qa_checks AS
SELECT 'ed_long_rows' AS check_name, count(*)::VARCHAR AS result FROM ed_long
UNION ALL SELECT 'unique_facility_measure', count(*)::VARCHAR FROM (
  SELECT facility_id, measure_id FROM ed_long GROUP BY 1,2 HAVING count(*) = 1
)
UNION ALL SELECT 'duplicate_facility_measure', count(*)::VARCHAR FROM (
  SELECT facility_id, measure_id FROM ed_long GROUP BY 1,2 HAVING count(*) > 1
)
UNION ALL SELECT 'ed_analytic_rows', count(*)::VARCHAR FROM ed_analytic
UNION ALL SELECT 'missing_hospital_join', count(*)::VARCHAR FROM ed_analytic WHERE facility_name IS NULL
UNION ALL SELECT 'invalid_negative_minutes', count(*)::VARCHAR FROM ed_analytic
  WHERE least(all_patient_ed_minutes, treat_release_ed_minutes, psychiatric_ed_minutes, transfer_ed_minutes) < 0
UNION ALL SELECT 'invalid_lwbs_percent', count(*)::VARCHAR FROM ed_analytic
  WHERE left_before_seen_pct < 0 OR left_before_seen_pct > 100;


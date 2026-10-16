# Analytic data dictionary

The processed file `data/processed/ed_analytic.csv` has one row per CMS facility ID.

| Variable | Type | Definition |
|---|---|---|
| `facility_id` | text | Six-character CMS Certification Number; leading zeros retained. |
| `facility_name` | text | CMS facility name. |
| `state` | text | Two-character state/territory abbreviation. |
| `hospital_type` | text | CMS hospital type classification. |
| `hospital_ownership` | text | CMS ownership classification. |
| `emergency_services` | text | Whether CMS lists emergency services. |
| `overall_rating` | integer | CMS overall hospital rating, when available. |
| `ed_volume` | category | CMS ED volume category: low, medium, high, very high. |
| `all_patient_ed_minutes` | numeric | OP-18a hospital median minutes. |
| `treat_release_ed_minutes` | numeric | OP-18b hospital median minutes. |
| `psychiatric_ed_minutes` | numeric | OP-18c hospital median minutes. |
| `transfer_ed_minutes` | numeric | OP-18d hospital median minutes. |
| `left_before_seen_pct` | numeric | OP-22 percentage leaving before being seen. |

Blank numeric fields represent unavailable, suppressed, or nonnumeric CMS values. They are not imputed.


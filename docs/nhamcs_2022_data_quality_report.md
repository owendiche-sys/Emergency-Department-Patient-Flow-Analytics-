# NHAMCS 2022 Data Quality Report

## Prepared dataset

- **Source file:** `data/raw/ed2022-stata.dta`
- **Prepared SQL handoff file:** `data/processed/nhamcs_2022_visits_clean.csv`
- **Rows:** 16,025
- **Columns:** 39
- **Duplicate visit IDs:** 0
- **Preparation script:** `src/prepare_nhamcs_csv.py`

The original CDC Stata file remains unchanged. The prepared SQL handoff CSV selects operationally useful fields, converts documented negative CDC special codes to blank values, supplies readable category labels, adds `visit_month_name` as a readable label, and creates two wait-time flags.

## Scope implications

The prepared dataset supports an **Emergency Department patient flow** project. Each row is one sampled ED visit, and the selected fields support analysis of ED arrival patterns, waiting times, triage urgency, ambulance arrival, visit length, admission outcomes, and patients leaving before care is completed.

The prepared dataset does **not** include a hospital department field and does not support readmission tracking. Do not build department-comparison KPIs, department tables, `vw_department_pressure`, busiest-department charts, or readmission summaries from this dataset. Use ED operational pressure metrics instead, such as arrival-hour volume, long-wait rates, wait time by triage level, ambulance-arrival patterns, admission outcomes, and left-without-being-seen rates.

## Waiting-time checks

- Valid waiting-time records: 13,272 (82.8%)
- Missing/not-applicable waiting-time records: 2,753
- Median valid wait: 14 minutes
- Mean valid wait: 36.0 minutes
- Valid range: 0–1280 minutes
- Four-hour waits (`> 240`): 238 (1.79% of valid waits)
- Two-hour waits (`>= 120`): 907 (6.83% of valid waits)

The four-hour target is valid but strongly imbalanced. Use stratified splitting and report precision, recall, F1 and PR-AUC rather than accuracy alone. The two-hour flag is provided as a more practical alternative for modelling; the final threshold should be documented before model development.

## Missing values

Blank values include genuine missing data and CDC special values such as Blank, Unknown and Not applicable. Zero remains a valid value where the CDC documentation defines it as one.

| Column | Missing | Percentage |
|---|---:|---:|
| `admission_destination` | 14,214 | 88.7% |
| `ambulance_transfer` | 13,637 | 85.1% |
| `pain_scale` | 7,055 | 44.0% |
| `triage_level` | 4,152 | 25.9% |
| `wait_time_minutes` | 2,753 | 17.2% |
| `extended_wait_2hr_flag` | 2,753 | 17.2% |
| `long_wait_4hr_flag` | 2,753 | 17.2% |
| `diastolic_bp` | 1,754 | 10.9% |
| `systolic_bp` | 1,722 | 10.7% |
| `pulse_bpm` | 1,053 | 6.6% |
| `oxygen_saturation` | 969 | 6.0% |
| `temperature_f` | 937 | 5.8% |
| `respiratory_rate` | 856 | 5.3% |
| `visit_length_minutes` | 697 | 4.3% |
| `arrival_by_ambulance` | 495 | 3.1% |
| `procedure_count` | 445 | 2.8% |
| `residence_type` | 262 | 1.6% |
| `chronic_condition_count` | 259 | 1.6% |
| `arrival_time` | 243 | 1.5% |
| `arrival_hour` | 243 | 1.5% |
| `primary_diagnosis_code` | 227 | 1.4% |
| `diagnosis_count` | 225 | 1.4% |
| `reason_for_visit_code` | 25 | 0.2% |

## Data-quality decisions already applied

- Generated a unique sequential `visit_id`; no duplicates were found.
- Preserved `arrival_time` as four-character HHMM text and derived `arrival_hour`.
- Converted the implied-decimal temperature encoding (for example, `984` to `98.4°F`).
- Converted nonnumeric Doppler/palpation codes in pulse and diastolic blood pressure to blank.
- Replaced documented negative missing/unknown/not-applicable codes with blank values.
- Retained CDC reason-for-visit and ICD diagnosis codes as codes rather than inventing labels.
- Retained `survey_visit_weight` for population-level estimates; it is not patient body weight.

## Modelling leakage warning

For a model intended to predict waiting time at or near arrival, do not use fields only known after care begins or ends. Exclude visit length, diagnoses, procedure count, admission/discharge outcomes, and departure status. Suitable candidate features include arrival month/day/hour, age, sex, residence type, ambulance arrival, triage level, initial pain score, and initial vital signs.

## SQL handoff notes

- Import blank CSV cells as `NULL`.
- Treat `visit_id` as the primary key.
- Store `arrival_time` as text or convert it carefully from HHMM.
- Keep `reason_for_visit_code` and `primary_diagnosis_code` as text identifiers.
- Store the two wait flags as nullable Boolean/bit values.
- Validate the imported row count against **16,025**.

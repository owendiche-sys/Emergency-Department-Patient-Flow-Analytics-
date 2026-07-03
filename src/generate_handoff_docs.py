"""Generate the NHAMCS CSV data dictionary and quality report for handoff."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "nhamcs_2022_visits.csv"
DOCS = ROOT / "docs"

DESCRIPTIONS = {
    "visit_id": "Project-generated unique identifier for each sampled ED visit.",
    "visit_month": "Calendar month of the visit (1–12).",
    "visit_day": "Day of week of the visit.",
    "arrival_time": "ED arrival time in HHMM format.",
    "arrival_hour": "Hour of ED arrival (0–23), derived from arrival_time.",
    "wait_time_minutes": "Minutes from ED arrival to first physician/APRN/PA contact.",
    "visit_length_minutes": "Total length of the ED visit in minutes.",
    "age_years": "Patient age in years; age 94 includes patients aged 94 and over.",
    "pain_scale": "Patient-reported pain score from 0 to 10.",
    "temperature_f": "Arrival temperature in degrees Fahrenheit.",
    "pulse_bpm": "Arrival pulse in beats per minute.",
    "respiratory_rate": "Arrival respiratory rate in breaths per minute.",
    "systolic_bp": "Arrival systolic blood pressure in mmHg.",
    "diastolic_bp": "Arrival diastolic blood pressure in mmHg.",
    "oxygen_saturation": "Arrival pulse oximetry percentage.",
    "chronic_condition_count": "Number of recorded chronic conditions.",
    "diagnosis_count": "Number of diagnoses recorded for the visit.",
    "procedure_count": "Number of procedures recorded for the visit.",
    "survey_visit_weight": "NHAMCS survey weight used to estimate national visit totals.",
    "sex": "Patient sex recorded as Female or Male in the source file.",
    "residence_type": "Patient residence category before the visit.",
    "arrival_by_ambulance": "Whether the patient arrived by ambulance.",
    "ambulance_transfer": "Whether an ambulance arrival was transferred from another facility.",
    "triage_level": "Recorded urgency category assigned during ED triage.",
    "reason_for_visit_code": "CDC reason-for-visit classification code.",
    "primary_diagnosis_code": "Primary ICD diagnosis code recorded for the visit.",
    "left_without_being_seen": "Whether the patient left before being seen.",
    "left_before_treatment_complete": "Whether the patient left before treatment was complete.",
    "left_against_medical_advice": "Whether the patient left against medical advice.",
    "died_in_ed": "Whether the patient died in the emergency department.",
    "admitted_to_hospital": "Whether the patient was admitted to the hospital.",
    "observation_then_hospitalized": "Whether observation was followed by hospitalization.",
    "observation_then_discharged": "Whether observation was followed by discharge.",
    "admission_destination": "Hospital unit to which the patient was admitted.",
    "region": "US Census region of the hospital.",
    "metropolitan_status": "Whether the hospital is in a metropolitan statistical area.",
    "long_wait_4hr_flag": "1 when valid wait_time_minutes is greater than 240; otherwise 0.",
    "extended_wait_2hr_flag": "1 when valid wait_time_minutes is at least 120; otherwise 0.",
}

POST_ARRIVAL = {
    "visit_length_minutes", "diagnosis_count", "procedure_count",
    "primary_diagnosis_code", "left_without_being_seen",
    "left_before_treatment_complete", "left_against_medical_advice", "died_in_ed",
    "admitted_to_hospital", "observation_then_hospitalized",
    "observation_then_discharged", "admission_destination",
}
TARGETS = {"wait_time_minutes", "long_wait_4hr_flag", "extended_wait_2hr_flag"}


def modelling_role(column: str) -> str:
    if column in TARGETS:
        return "Target/measurement"
    if column in POST_ARRIVAL:
        return "Post-arrival outcome; exclude from wait prediction"
    if column in {"visit_id", "survey_visit_weight"}:
        return "Identifier/analysis metadata; exclude from ML features"
    return "Candidate arrival-time feature"


def main() -> None:
    df = pd.read_csv(DATA, dtype={"arrival_time": "string", "primary_diagnosis_code": "string"})
    DOCS.mkdir(parents=True, exist_ok=True)

    dictionary = pd.DataFrame(
        {
            "column": df.columns,
            "csv_type": [str(df[c].dtype) for c in df.columns],
            "description": [DESCRIPTIONS[c] for c in df.columns],
            "modelling_role": [modelling_role(c) for c in df.columns],
        }
    )
    dictionary.to_csv(DOCS / "nhamcs_2022_data_dictionary.csv", index=False)

    missing = df.isna().sum().sort_values(ascending=False)
    missing_rows = "\n".join(
        f"| `{column}` | {count:,} | {count / len(df):.1%} |"
        for column, count in missing.items()
        if count
    )
    valid_wait = df["wait_time_minutes"].dropna()
    four_hour = int(df["long_wait_4hr_flag"].sum())
    two_hour = int(df["extended_wait_2hr_flag"].sum())

    report = f"""# NHAMCS 2022 Data Quality Report

## Prepared dataset

- **Source file:** `data/raw/ed2022-stata.dta`
- **Prepared file:** `data/processed/nhamcs_2022_visits.csv`
- **Rows:** {len(df):,}
- **Columns:** {len(df.columns)}
- **Duplicate visit IDs:** {df['visit_id'].duplicated().sum():,}
- **Preparation script:** `src/prepare_nhamcs_csv.py`

The original CDC Stata file remains unchanged. The prepared CSV selects operationally useful fields, converts documented negative CDC special codes to blank values, supplies readable category labels, and creates two wait-time flags.

## Waiting-time checks

- Valid waiting-time records: {len(valid_wait):,} ({len(valid_wait) / len(df):.1%})
- Missing/not-applicable waiting-time records: {df['wait_time_minutes'].isna().sum():,}
- Median valid wait: {valid_wait.median():.0f} minutes
- Mean valid wait: {valid_wait.mean():.1f} minutes
- Valid range: {valid_wait.min():.0f}–{valid_wait.max():.0f} minutes
- Four-hour waits (`> 240`): {four_hour:,} ({four_hour / len(valid_wait):.2%} of valid waits)
- Two-hour waits (`>= 120`): {two_hour:,} ({two_hour / len(valid_wait):.2%} of valid waits)

The four-hour target is valid but strongly imbalanced. Use stratified splitting and report precision, recall, F1 and PR-AUC rather than accuracy alone. The two-hour flag is provided as a more practical alternative for modelling; the final threshold should be documented before model development.

## Missing values

Blank values include genuine missing data and CDC special values such as Blank, Unknown and Not applicable. Zero remains a valid value where the CDC documentation defines it as one.

| Column | Missing | Percentage |
|---|---:|---:|
{missing_rows}

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
- Validate the imported row count against **{len(df):,}**.
"""
    (DOCS / "nhamcs_2022_data_quality_report.md").write_text(report, encoding="utf-8")
    print("Created data dictionary and quality report")


if __name__ == "__main__":
    main()

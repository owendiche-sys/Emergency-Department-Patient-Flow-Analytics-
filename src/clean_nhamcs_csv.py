"""Clean the prepared NHAMCS CSV for SQL handoff.

The prepared file intentionally keeps CDC missing/unknown values as blanks.
This script makes that missingness explicit for SQL import without inventing
clinical measurements.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "processed" / "nhamcs_2022_visits.csv"
DEFAULT_OUTPUT = ROOT / "data" / "processed" / "nhamcs_2022_visits_clean.csv"
DEFAULT_REPORT = ROOT / "docs" / "nhamcs_2022_cleaning_report.json"

NULL_TOKEN = "NULL"

MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

TEXT_COLUMNS = [
    "visit_day",
    "arrival_time",
    "sex",
    "residence_type",
    "arrival_by_ambulance",
    "ambulance_transfer",
    "triage_level",
    "primary_diagnosis_code",
    "left_without_being_seen",
    "left_before_treatment_complete",
    "left_against_medical_advice",
    "died_in_ed",
    "admitted_to_hospital",
    "observation_then_hospitalized",
    "observation_then_discharged",
    "admission_destination",
    "region",
    "metropolitan_status",
]

INT_COLUMNS = [
    "visit_id",
    "visit_month",
    "arrival_hour",
    "age_years",
    "chronic_condition_count",
    "diagnosis_count",
    "procedure_count",
    "reason_for_visit_code",
    "long_wait_4hr_flag",
    "extended_wait_2hr_flag",
]

FLOAT_COLUMNS = [
    "wait_time_minutes",
    "visit_length_minutes",
    "pain_scale",
    "pulse_bpm",
    "respiratory_rate",
    "systolic_bp",
    "diastolic_bp",
    "oxygen_saturation",
    "survey_visit_weight",
    "temperature_f",
]

EXPECTED_COLUMNS = TEXT_COLUMNS + INT_COLUMNS + FLOAT_COLUMNS

FILL_VALUES = {
    "arrival_by_ambulance": "Unknown",
    "ambulance_transfer": "Not applicable or unknown",
    "triage_level": "Unknown",
    "residence_type": "Unknown",
    "admission_destination": "Not admitted or unknown",
    "primary_diagnosis_code": "Unknown",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a SQL-ready clean copy of the prepared NHAMCS CSV."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--null-token",
        default=NULL_TOKEN,
        help="Token written for missing numeric values. Default: NULL.",
    )
    return parser.parse_args()


def normalize_arrival_time(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.replace({"": pd.NA, "nan": pd.NA, "NaN": pd.NA})
    numeric = pd.to_numeric(cleaned, errors="coerce")
    padded = numeric.astype("Int64").astype("string").str.zfill(4)
    normalized = (
        pd.to_numeric(padded.str.slice(0, 2), errors="coerce").astype("Int64").astype("string")
        + ":"
        + padded.str.slice(2, 4)
    )
    return normalized.where(numeric.notna(), pd.NA)


def clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(df.columns))
    extra_columns = sorted(set(df.columns) - set(EXPECTED_COLUMNS))
    if missing_columns:
        raise ValueError(f"Input is missing expected columns: {missing_columns}")

    original_rows = len(df)
    original_columns = len(df.columns)
    original_blank_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    duplicate_visit_ids = int(df["visit_id"].duplicated().sum())

    df = df.drop_duplicates().copy()

    for column in TEXT_COLUMNS:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace({"": pd.NA})

    df["arrival_time"] = normalize_arrival_time(df["arrival_time"])

    for column, value in FILL_VALUES.items():
        df[column] = df[column].fillna(value)

    for column in INT_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

    for column in FLOAT_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["visit_month_name"] = df["visit_month"].map(MONTH_NAMES).astype("string")

    # Keep the derived hour aligned with H:MM when arrival_time is available.
    derived_hour = pd.to_numeric(df["arrival_time"].str.split(":").str[0], errors="coerce").astype("Int64")
    df["arrival_hour"] = df["arrival_hour"].fillna(derived_hour).astype("Int64")

    output_columns = list(df.columns)
    output_columns.insert(output_columns.index("visit_month") + 1, output_columns.pop(output_columns.index("visit_month_name")))
    df = df[output_columns]

    remaining_missing = df.isna().sum()
    report = {
        "input_rows": original_rows,
        "output_rows": len(df),
        "input_columns": original_columns,
        "output_columns": len(df.columns),
        "duplicate_rows_removed": duplicate_rows,
        "duplicate_visit_ids_found": duplicate_visit_ids,
        "input_blank_cells": original_blank_cells,
        "output_blank_cells_before_null_token": int(remaining_missing.sum()),
        "columns_filled_with_labels": FILL_VALUES,
        "missing_by_column_before_null_token": {
            column: int(count)
            for column, count in remaining_missing.sort_values(ascending=False).items()
            if count > 0
        },
        "extra_columns": extra_columns,
    }
    return df, report


def write_clean_csv(df: pd.DataFrame, output: Path, null_token: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    df.astype("object").where(df.notna(), null_token).to_csv(output, index=False)


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input, dtype="string", keep_default_na=True)
    cleaned, report = clean_dataframe(df)

    write_clean_csv(cleaned, args.output, args.null_token)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Created {args.output}")
    print(f"Created {args.report}")
    print(f"Rows: {report['input_rows']:,} input -> {report['output_rows']:,} output")
    print(f"Blank cells converted to {args.null_token!r}: {report['output_blank_cells_before_null_token']:,}")


if __name__ == "__main__":
    main()

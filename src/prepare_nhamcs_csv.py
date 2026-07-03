"""Create a focused, SQL-friendly visit table from the 2022 NHAMCS file."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "ed2022-stata.dta"
OUTPUT = ROOT / "data" / "processed" / "nhamcs_2022_visits.csv"

SOURCE_COLUMNS = [
    "VMONTH", "VDAYR", "ARRTIME", "WAITTIME", "LOV", "AGE", "SEX",
    "RESIDNCE", "ARREMS", "AMBTRANSFER", "IMMEDR", "PAINSCALE",
    "TEMPF", "PULSE", "RESPR", "BPSYS", "BPDIAS", "POPCT",
    "RFV1", "DIAG1", "TOTCHRON", "TOTDIAG", "TOTPROC", "LWBS",
    "LBTC", "LEFTAMA", "DIEDED", "ADMITHOS", "OBSHOS", "OBSDIS",
    "ADMIT", "REGION", "MSA", "PATWT",
]


def labelled(series: pd.Series, mapping: dict[int, str]) -> pd.Series:
    """Map documented CDC codes to readable labels; special codes become blank."""
    return series.map(mapping).astype("string")


def main() -> None:
    df = pd.read_stata(INPUT, columns=SOURCE_COLUMNS, convert_categoricals=False)

    result = pd.DataFrame({"visit_id": range(1, len(df) + 1)})
    result["visit_month"] = df["VMONTH"]
    result["visit_day"] = labelled(
        df["VDAYR"],
        {1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday",
         5: "Thursday", 6: "Friday", 7: "Saturday"},
    )

    arrival = df["ARRTIME"].astype("string").where(df["ARRTIME"] != "-9")
    result["arrival_time"] = arrival.str.zfill(4)
    result["arrival_hour"] = pd.to_numeric(arrival.str[:-2], errors="coerce").astype("Int64")

    for source, target in {
        "WAITTIME": "wait_time_minutes",
        "LOV": "visit_length_minutes",
        "AGE": "age_years",
        "PAINSCALE": "pain_scale",
        "PULSE": "pulse_bpm",
        "RESPR": "respiratory_rate",
        "BPSYS": "systolic_bp",
        "BPDIAS": "diastolic_bp",
        "POPCT": "oxygen_saturation",
        "TOTCHRON": "chronic_condition_count",
        "TOTDIAG": "diagnosis_count",
        "TOTPROC": "procedure_count",
        "PATWT": "survey_visit_weight",
    }.items():
        result[target] = pd.to_numeric(df[source], errors="coerce").where(df[source] >= 0)

    # CDC stores Fahrenheit with one implied decimal place (984 means 98.4°F).
    result["temperature_f"] = df["TEMPF"].where(df["TEMPF"] >= 0) / 10
    # 998 represents a Doppler/palpation reading rather than a numeric measurement.
    result.loc[df["PULSE"] == 998, "pulse_bpm"] = pd.NA
    result.loc[df["BPDIAS"] == 998, "diastolic_bp"] = pd.NA

    result["sex"] = labelled(df["SEX"], {1: "Female", 2: "Male"})
    result["residence_type"] = labelled(
        df["RESIDNCE"],
        {1: "Private residence", 2: "Nursing home",
         3: "Homeless/homeless shelter", 4: "Other"},
    )
    result["arrival_by_ambulance"] = labelled(df["ARREMS"], {1: "Yes", 2: "No"})
    result["ambulance_transfer"] = labelled(df["AMBTRANSFER"], {1: "Yes", 2: "No"})
    result["triage_level"] = labelled(
        df["IMMEDR"],
        {0: "No triage", 1: "Immediate", 2: "Emergent", 3: "Urgent",
         4: "Semi-urgent", 5: "Nonurgent", 7: "Facility does not conduct triage"},
    )

    result["reason_for_visit_code"] = df["RFV1"].where(df["RFV1"] >= 0)
    result["primary_diagnosis_code"] = df["DIAG1"].astype("string").replace({"-9": pd.NA})

    for source, target in {
        "LWBS": "left_without_being_seen",
        "LBTC": "left_before_treatment_complete",
        "LEFTAMA": "left_against_medical_advice",
        "DIEDED": "died_in_ed",
        "ADMITHOS": "admitted_to_hospital",
        "OBSHOS": "observation_then_hospitalized",
        "OBSDIS": "observation_then_discharged",
    }.items():
        result[target] = df[source].map({0: "No", 1: "Yes"}).astype("string")

    result["admission_destination"] = labelled(
        df["ADMIT"],
        {1: "Critical care unit", 2: "Stepdown unit", 3: "Operating room",
         4: "Mental health or detox unit", 5: "Cardiac catheterization lab",
         6: "Other bed/unit"},
    )
    result["region"] = labelled(df["REGION"], {1: "Northeast", 2: "Midwest", 3: "South", 4: "West"})
    result["metropolitan_status"] = labelled(df["MSA"], {1: "Metropolitan", 2: "Non-metropolitan"})

    result["long_wait_4hr_flag"] = result["wait_time_minutes"].gt(240).astype("Int64")
    result["extended_wait_2hr_flag"] = result["wait_time_minutes"].ge(120).astype("Int64")
    result.loc[result["wait_time_minutes"].isna(), ["long_wait_4hr_flag", "extended_wait_2hr_flag"]] = pd.NA

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT, index=False)
    print(f"Created {OUTPUT} with {len(result):,} rows and {len(result.columns)} columns")


if __name__ == "__main__":
    main()

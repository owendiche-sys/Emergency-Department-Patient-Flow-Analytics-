from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "nhamcs_2022_visits_clean.csv"
FIGURE_DIR = PROJECT_ROOT / "outputs" / "figures"
MODEL_METRICS_PATH = PROJECT_ROOT / "outputs" / "models" / "week5_wait_prediction_model_metrics.csv"


st.set_page_config(
    page_title="ED Patient Flow Analytics",
    page_icon="",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, na_values=["NULL", "", " "])
    df["extended_wait_2hr_flag"] = df["extended_wait_2hr_flag"].fillna(0).astype(int)
    df["long_wait_4hr_flag"] = df["long_wait_4hr_flag"].fillna(0).astype(int)
    return df


@st.cache_data
def load_model_metrics() -> pd.DataFrame:
    if MODEL_METRICS_PATH.exists():
        return pd.read_csv(MODEL_METRICS_PATH)
    return pd.DataFrame()


def rate(series: pd.Series) -> float:
    valid = series.dropna()
    if valid.empty:
        return 0.0
    return (valid.eq("Yes").mean()) * 100


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    months = sorted(df["visit_month_name"].dropna().unique().tolist())
    selected_months = st.sidebar.multiselect("Month", months, default=months)

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    available_days = [day for day in days if day in set(df["visit_day"].dropna())]
    selected_days = st.sidebar.multiselect("Day", available_days, default=available_days)

    triage_levels = sorted(df["triage_level"].dropna().unique().tolist())
    selected_triage = st.sidebar.multiselect("Triage level", triage_levels, default=triage_levels)

    ambulance_values = sorted(df["arrival_by_ambulance"].dropna().unique().tolist())
    selected_ambulance = st.sidebar.multiselect(
        "Arrival by ambulance",
        ambulance_values,
        default=ambulance_values,
    )

    regions = sorted(df["region"].dropna().unique().tolist())
    selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

    min_hour = int(df["arrival_hour"].dropna().min())
    max_hour = int(df["arrival_hour"].dropna().max())
    selected_hours = st.sidebar.slider(
        "Arrival hour",
        min_value=min_hour,
        max_value=max_hour,
        value=(min_hour, max_hour),
    )

    filtered = df[
        df["visit_month_name"].isin(selected_months)
        & df["visit_day"].isin(selected_days)
        & df["triage_level"].isin(selected_triage)
        & df["arrival_by_ambulance"].isin(selected_ambulance)
        & df["region"].isin(selected_regions)
        & df["arrival_hour"].between(selected_hours[0], selected_hours[1])
    ].copy()

    return filtered


def kpi_cards(df: pd.DataFrame) -> None:
    valid_waits = df["wait_time_minutes"].dropna()
    total_visits = len(df)
    two_hour_rate = df.loc[df["wait_time_minutes"].notna(), "extended_wait_2hr_flag"].mean() * 100
    four_hour_rate = df.loc[df["wait_time_minutes"].notna(), "long_wait_4hr_flag"].mean() * 100

    cols = st.columns(5)
    cols[0].metric("ED visits", f"{total_visits:,}")
    cols[1].metric("Median wait", f"{valid_waits.median():.0f} min" if not valid_waits.empty else "n/a")
    cols[2].metric("Average wait", f"{valid_waits.mean():.1f} min" if not valid_waits.empty else "n/a")
    cols[3].metric("2-hour wait rate", f"{two_hour_rate:.2f}%" if pd.notna(two_hour_rate) else "n/a")
    cols[4].metric("4-hour wait rate", f"{four_hour_rate:.2f}%" if pd.notna(four_hour_rate) else "n/a")

    cols = st.columns(4)
    cols[0].metric("Admission rate", f"{rate(df['admitted_to_hospital']):.2f}%")
    cols[1].metric("LWBS rate", f"{rate(df['left_without_being_seen']):.2f}%")
    cols[2].metric("LBTC rate", f"{rate(df['left_before_treatment_complete']):.2f}%")
    cols[3].metric("Ambulance rate", f"{rate(df['arrival_by_ambulance']):.2f}%")


def overview_page(df: pd.DataFrame) -> None:
    st.title("ED Patient Flow Analytics")
    kpi_cards(df)

    left, right = st.columns(2)
    with left:
        monthly = df.groupby(["visit_month", "visit_month_name"]).size().reset_index(name="visits")
        monthly = monthly.sort_values("visit_month").set_index("visit_month_name")
        st.subheader("Visits by Month")
        st.bar_chart(monthly["visits"])

    with right:
        hourly = df.groupby("arrival_hour").size().reset_index(name="visits").set_index("arrival_hour")
        st.subheader("Visits by Arrival Hour")
        st.line_chart(hourly["visits"])


def patient_flow_page(df: pd.DataFrame) -> None:
    st.title("ED Patient Flow")

    month_summary = (
        df.groupby(["visit_month", "visit_month_name"])
        .agg(
            patient_count=("visit_id", "count"),
            avg_wait=("wait_time_minutes", "mean"),
            avg_visit_length=("visit_length_minutes", "mean"),
        )
        .reset_index()
        .sort_values("visit_month")
    )

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_summary = (
        df.groupby("visit_day")
        .agg(
            patient_count=("visit_id", "count"),
            avg_wait=("wait_time_minutes", "mean"),
            avg_visit_length=("visit_length_minutes", "mean"),
        )
        .reindex(day_order)
        .dropna(how="all")
    )

    hour_summary = (
        df.groupby("arrival_hour")
        .agg(
            patient_count=("visit_id", "count"),
            avg_wait=("wait_time_minutes", "mean"),
            avg_visit_length=("visit_length_minutes", "mean"),
        )
        .reset_index()
        .set_index("arrival_hour")
    )

    st.subheader("Monthly Summary")
    st.dataframe(
        month_summary.rename(
            columns={
                "visit_month_name": "month",
                "patient_count": "visits",
                "avg_wait": "avg wait",
                "avg_visit_length": "avg visit length",
            }
        )[["month", "visits", "avg wait", "avg visit length"]],
        hide_index=True,
        use_container_width=True,
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Visits by Day")
        st.bar_chart(day_summary["patient_count"])
    with right:
        st.subheader("Visits by Arrival Hour")
        st.line_chart(hour_summary["patient_count"])


def waiting_time_page(df: pd.DataFrame) -> None:
    st.title("Waiting Time Analysis")
    kpi_cards(df)

    wait_by_triage = (
        df.dropna(subset=["wait_time_minutes"])
        .groupby("triage_level")["wait_time_minutes"]
        .median()
        .sort_values(ascending=False)
    )
    st.subheader("Median Wait by Triage Level")
    st.bar_chart(wait_by_triage)

    wait_by_region = (
        df.dropna(subset=["wait_time_minutes"])
        .groupby("region")["wait_time_minutes"]
        .median()
        .sort_values(ascending=False)
    )
    st.subheader("Median Wait by Region")
    st.bar_chart(wait_by_region)


def triage_page(df: pd.DataFrame) -> None:
    st.title("Triage and Acuity")

    triage_summary = (
        df.groupby("triage_level")
        .agg(
            patient_count=("visit_id", "count"),
            avg_wait=("wait_time_minutes", "mean"),
            median_wait=("wait_time_minutes", "median"),
            avg_visit_length=("visit_length_minutes", "mean"),
            admission_rate=("admitted_to_hospital", lambda values: rate(values)),
        )
        .sort_values("patient_count", ascending=False)
    )

    st.dataframe(
        triage_summary.rename(
            columns={
                "patient_count": "visits",
                "avg_wait": "avg wait",
                "median_wait": "median wait",
                "avg_visit_length": "avg visit length",
                "admission_rate": "admission rate",
            }
        ).round(2),
        use_container_width=True,
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Visits by Triage Level")
        st.bar_chart(triage_summary["patient_count"])
    with right:
        st.subheader("Admission Rate by Triage Level")
        st.bar_chart(triage_summary["admission_rate"])


def outcomes_page(df: pd.DataFrame) -> None:
    st.title("Outcomes")

    outcome_rates = pd.Series(
        {
            "Admitted to hospital": rate(df["admitted_to_hospital"]),
            "Observation then hospitalized": rate(df["observation_then_hospitalized"]),
            "Observation then discharged": rate(df["observation_then_discharged"]),
            "Left without being seen": rate(df["left_without_being_seen"]),
            "Left before treatment complete": rate(df["left_before_treatment_complete"]),
        }
    )
    st.bar_chart(outcome_rates)


def ml_page(df: pd.DataFrame) -> None:
    st.title("ML Prediction")
    metrics_df = load_model_metrics()

    target_counts = pd.DataFrame(
        {
            "target": ["2-hour extended wait", "4-hour long wait"],
            "positive_cases": [
                int(df["extended_wait_2hr_flag"].sum()),
                int(df["long_wait_4hr_flag"].sum()),
            ],
            "positive_rate": [
                df["extended_wait_2hr_flag"].mean() * 100,
                df["long_wait_4hr_flag"].mean() * 100,
            ],
        }
    )

    st.dataframe(target_counts, hide_index=True, use_container_width=True)

    if metrics_df.empty:
        st.info("Run `python src/train_wait_prediction_models.py` to generate Week 5 model metrics.")
    else:
        display_columns = ["model", "accuracy", "precision", "recall", "f1", "roc_auc"]
        st.subheader("Model Comparison")
        st.dataframe(metrics_df[display_columns].round(3), hide_index=True, use_container_width=True)

        confusion_columns = ["model", "true_negative", "false_positive", "false_negative", "true_positive"]
        st.subheader("Confusion Matrix Counts")
        st.dataframe(metrics_df[confusion_columns], hide_index=True, use_container_width=True)

    st.caption(
        "The 2-hour target is the primary model target because the 4-hour target is highly imbalanced. "
        "Post-arrival outcomes are excluded from the feature list."
    )


def sql_insights_page(df: pd.DataFrame) -> None:
    st.title("SQL Insights")
    st.caption("Dashboard sections are aligned to the SQL views in `sql/05_views_for_python.sql`.")

    view_map = pd.DataFrame(
        [
            ("vw_ed_patient_flow_summary", "Overview KPI cards"),
            ("vw_ed_wait_kpis", "Waiting Time Analysis"),
            ("vw_ed_triage_flow", "Triage and Acuity"),
            ("vw_ed_outcomes", "Outcomes"),
            ("vw_business_question_metrics", "Business Recommendations"),
            ("vw_ml_wait_features", "ML Prediction"),
            ("vw_ambulance_summary", "Overview and patient flow filters"),
            ("vw_region_summary", "Waiting Time Analysis"),
            ("vw_monthly_summary", "ED Patient Flow"),
            ("vw_day_summary", "ED Patient Flow"),
            ("vw_arrival_hour_summary", "ED Patient Flow"),
        ],
        columns=["SQL view", "dashboard use"],
    )
    st.dataframe(view_map, hide_index=True, use_container_width=True)

    business_metrics = pd.DataFrame(
        {
            "metric": [
                "Total visits",
                "Average wait minutes",
                "Average visit length minutes",
                "Admission rate",
                "Ambulance arrival rate",
                "2-hour extended wait rate",
                "4-hour long wait rate",
                "Left without being seen rate",
                "Left before treatment complete rate",
            ],
            "value": [
                len(df),
                df["wait_time_minutes"].mean(),
                df["visit_length_minutes"].mean(),
                rate(df["admitted_to_hospital"]),
                rate(df["arrival_by_ambulance"]),
                df.loc[df["wait_time_minutes"].notna(), "extended_wait_2hr_flag"].mean() * 100,
                df.loc[df["wait_time_minutes"].notna(), "long_wait_4hr_flag"].mean() * 100,
                rate(df["left_without_being_seen"]),
                rate(df["left_before_treatment_complete"]),
            ],
        }
    )
    st.subheader("Business Question Metrics")
    st.dataframe(business_metrics.round(2), hide_index=True, use_container_width=True)


def recommendations_page() -> None:
    st.title("Business Recommendations")
    st.markdown(
        """
        - Use predictable arrival peaks to plan staffing and operational readiness.
        - Track 2-hour and 4-hour wait thresholds separately because they describe different levels of pressure.
        - Monitor waits by triage, region, metropolitan status, and ambulance arrival to identify operational variation.
        - Keep admission and departure outcomes in reporting, not arrival-time prediction features.
        """
    )


df = load_data()

page = st.sidebar.radio(
    "Dashboard page",
    [
        "Overview",
        "ED Patient Flow",
        "Waiting Time Analysis",
        "Triage and Acuity",
        "Outcomes",
        "SQL Insights",
        "ML Prediction",
        "Business Recommendations",
    ],
)

filtered_df = apply_filters(df)

if page == "Overview":
    overview_page(filtered_df)
elif page == "ED Patient Flow":
    patient_flow_page(filtered_df)
elif page == "Waiting Time Analysis":
    waiting_time_page(filtered_df)
elif page == "Triage and Acuity":
    triage_page(filtered_df)
elif page == "Outcomes":
    outcomes_page(filtered_df)
elif page == "SQL Insights":
    sql_insights_page(filtered_df)
elif page == "ML Prediction":
    ml_page(filtered_df)
else:
    recommendations_page()

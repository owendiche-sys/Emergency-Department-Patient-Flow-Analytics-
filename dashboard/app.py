from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "nhamcs_2022_visits_clean.csv"
FIGURE_DIR = PROJECT_ROOT / "outputs" / "figures"


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

    filtered = df[
        df["visit_month_name"].isin(selected_months)
        & df["visit_day"].isin(selected_days)
        & df["triage_level"].isin(selected_triage)
        & df["arrival_by_ambulance"].isin(selected_ambulance)
        & df["region"].isin(selected_regions)
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
    st.info(
        "The Week 4 notebook uses the 2-hour extended-wait flag as the first ML target. "
        "SQL-backed model features should be connected after Nimi provides vw_ml_wait_features."
    )


def sql_insights_page() -> None:
    st.title("SQL Insights")
    st.warning(
        "SQL KPI queries and final SQL views will be connected here. "
        "This CSV-backed dashboard page is a placeholder for the SQL Insights section."
    )


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
        "Waiting Time Analysis",
        "Outcomes",
        "SQL Insights",
        "ML Prediction",
        "Business Recommendations",
    ],
)

filtered_df = apply_filters(df)

if page == "Overview":
    overview_page(filtered_df)
elif page == "Waiting Time Analysis":
    waiting_time_page(filtered_df)
elif page == "Outcomes":
    outcomes_page(filtered_df)
elif page == "SQL Insights":
    sql_insights_page()
elif page == "ML Prediction":
    ml_page(filtered_df)
else:
    recommendations_page()

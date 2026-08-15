"""Public Streamlit dashboard for the ED Patient Flow Analytics project."""

from __future__ import annotations

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "nhamcs_2022_visits_clean.csv"
MODEL_METRICS_PATH = PROJECT_ROOT / "outputs" / "models" / "wait_prediction_model_metrics.csv"
TARGET_BALANCE_PATH = PROJECT_ROOT / "outputs" / "models" / "wait_target_balance.csv"

NAVY = "#17324D"
TEAL = "#0F766E"
BLUE = "#2563EB"
GOLD = "#B7791F"
RED = "#B42318"
SLATE = "#475569"
LIGHT_BLUE = "#DBEAFE"
LIGHT_TEAL = "#CCFBF1"
MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TRIAGE_ORDER = [
    "Immediate",
    "Emergent",
    "Urgent",
    "Semi-urgent",
    "Nonurgent",
    "No triage",
    "Facility does not conduct triage",
    "Unknown",
]


st.set_page_config(
    page_title="ED Patient Flow Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --brand-navy: #17324D;
        --brand-teal: #0F766E;
        --surface: #FFFFFF;
        --surface-soft: #F4F7FA;
        --border: #D9E2EC;
        --text: #102A43;
        --muted: #526777;
    }
    .stApp { background: var(--surface-soft); color: var(--text); }
    [data-testid="stHeader"] { background: rgba(244, 247, 250, 0.92); }
    [data-testid="stSidebar"] { background: #F8FAFC; border-right: 1px solid var(--border); }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: var(--brand-navy); }
    .block-container { max-width: 1440px; padding-top: 4.5rem; padding-bottom: 3rem; }
    h1, h2, h3 { color: var(--brand-navy); letter-spacing: -0.015em; }
    p, li { line-height: 1.6; }
    .eyebrow {
        color: var(--brand-teal);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    .page-summary { color: var(--muted); max-width: 78ch; margin-bottom: 1.25rem; }
    .status-chip {
        display: inline-block;
        padding: 0.3rem 0.65rem;
        border-radius: 999px;
        background: #E6FFFA;
        border: 1px solid #99F6E4;
        color: #115E59;
        font-size: 0.78rem;
        font-weight: 700;
    }
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        box-shadow: 0 1px 2px rgba(16, 42, 67, 0.06);
    }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: var(--brand-navy); font-variant-numeric: tabular-nums; }
    [data-testid="stDataFrame"] { background: var(--surface); border-radius: 10px; }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface);
        border-color: var(--border);
        border-radius: 12px;
    }
    .insight-card {
        height: 100%;
        padding: 1rem 1.1rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        background: var(--surface);
    }
    .insight-card strong { color: var(--brand-navy); }
    .insight-card p { color: var(--muted); margin: 0.35rem 0 0; }
    .method-step {
        min-height: 118px;
        padding: 1rem;
        border-top: 4px solid var(--brand-teal);
        border-radius: 10px;
        background: var(--surface);
        box-shadow: 0 1px 2px rgba(16, 42, 67, 0.06);
    }
    .method-step strong { color: var(--brand-navy); }
    .method-step p { color: var(--muted); margin-bottom: 0; }
    .footer-note {
        color: var(--muted);
        font-size: 0.84rem;
        border-top: 1px solid var(--border);
        padding-top: 1rem;
        margin-top: 2rem;
    }
    @media (max-width: 768px) {
        .block-container { padding: 4rem 0.8rem 2rem; }
        h1 { font-size: 2rem !important; }
        .page-summary { font-size: 0.96rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


REQUIRED_COLUMNS = {
    "visit_id",
    "visit_month",
    "visit_month_name",
    "visit_day",
    "arrival_hour",
    "wait_time_minutes",
    "visit_length_minutes",
    "age_years",
    "sex",
    "arrival_by_ambulance",
    "triage_level",
    "region",
    "metropolitan_status",
    "extended_wait_2hr_flag",
    "long_wait_4hr_flag",
    "admitted_to_hospital",
    "left_without_being_seen",
    "left_before_treatment_complete",
}


@st.cache_data(show_spinner="Loading ED visit data...")
def load_data() -> pd.DataFrame:
    """Load and validate the deployment-ready analytical dataset."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Required data file was not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH, na_values=["NULL", "", " "])
    missing_columns = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing_columns:
        raise ValueError(f"The analytical dataset is missing required columns: {missing_columns}")

    numeric_columns = [
        "visit_month",
        "arrival_hour",
        "wait_time_minutes",
        "visit_length_minutes",
        "age_years",
        "extended_wait_2hr_flag",
        "long_wait_4hr_flag",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["age_group"] = pd.cut(
        df["age_years"],
        bins=[-1, 17, 34, 49, 64, float("inf")],
        labels=["0-17", "18-34", "35-49", "50-64", "65+"],
    )
    df["arrival_period"] = pd.cut(
        df["arrival_hour"],
        bins=[-1, 5, 11, 17, 23],
        labels=["Overnight", "Morning", "Afternoon", "Evening"],
    ).astype("string").fillna("Unknown")
    return df


@st.cache_data(show_spinner=False)
def load_model_metrics() -> pd.DataFrame:
    if not MODEL_METRICS_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(MODEL_METRICS_PATH)


@st.cache_data(show_spinner=False)
def load_target_balance() -> pd.DataFrame:
    if not TARGET_BALANCE_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(TARGET_BALANCE_PATH)


def page_intro(eyebrow: str, title: str, description: str) -> None:
    st.markdown(f'<div class="eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<p class="page-summary">{description}</p>', unsafe_allow_html=True)


def yes_rate(series: pd.Series) -> float:
    valid = series.dropna()
    return float(valid.eq("Yes").mean() * 100) if not valid.empty else float("nan")


def wait_flag_rate(df: pd.DataFrame, flag: str) -> float:
    valid = df.loc[df["wait_time_minutes"].notna(), flag].dropna()
    return float(valid.mean() * 100) if not valid.empty else float("nan")


def format_percentage(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value:.2f}%"


def kpi_cards(df: pd.DataFrame) -> None:
    valid_waits = df["wait_time_minutes"].dropna()
    first_row = st.columns(5)
    first_row[0].metric("Sample visits", f"{len(df):,}")
    first_row[1].metric("Valid wait records", f"{len(valid_waits):,}")
    first_row[2].metric("Median wait", f"{valid_waits.median():.0f} min" if not valid_waits.empty else "n/a")
    first_row[3].metric("2-hour wait rate", format_percentage(wait_flag_rate(df, "extended_wait_2hr_flag")))
    first_row[4].metric("4-hour wait rate", format_percentage(wait_flag_rate(df, "long_wait_4hr_flag")))

    second_row = st.columns(4)
    second_row[0].metric("Average visit length", f"{df['visit_length_minutes'].mean():.1f} min")
    second_row[1].metric("Admission rate", format_percentage(yes_rate(df["admitted_to_hospital"])))
    second_row[2].metric("LWBS rate", format_percentage(yes_rate(df["left_without_being_seen"])))
    second_row[3].metric("Ambulance arrival", format_percentage(yes_rate(df["arrival_by_ambulance"])))


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    filter_keys = [
        "filter_months",
        "filter_days",
        "filter_triage",
        "filter_ambulance",
        "filter_regions",
        "filter_metro",
        "filter_sex",
        "filter_hours",
    ]
    if st.sidebar.button("Reset all filters", width="stretch"):
        for key in filter_keys:
            st.session_state.pop(key, None)
        st.rerun()

    st.sidebar.subheader("Filter the sample")
    month_lookup = (
        df[["visit_month", "visit_month_name"]]
        .drop_duplicates()
        .sort_values("visit_month")["visit_month_name"]
        .dropna()
        .tolist()
    )
    selected_months = st.sidebar.multiselect(
        "Month", month_lookup, default=month_lookup, key="filter_months"
    )
    available_days = [day for day in DAY_ORDER if day in set(df["visit_day"].dropna())]
    selected_days = st.sidebar.multiselect(
        "Arrival day", available_days, default=available_days, key="filter_days"
    )
    available_triage = [level for level in TRIAGE_ORDER if level in set(df["triage_level"].dropna())]
    selected_triage = st.sidebar.multiselect(
        "Triage level", available_triage, default=available_triage, key="filter_triage"
    )
    ambulance_values = sorted(df["arrival_by_ambulance"].dropna().unique().tolist())
    selected_ambulance = st.sidebar.multiselect(
        "Arrival by ambulance",
        ambulance_values,
        default=ambulance_values,
        key="filter_ambulance",
    )
    regions = sorted(df["region"].dropna().unique().tolist())
    selected_regions = st.sidebar.multiselect(
        "Region", regions, default=regions, key="filter_regions"
    )
    metro_values = sorted(df["metropolitan_status"].dropna().unique().tolist())
    selected_metro = st.sidebar.multiselect(
        "Metropolitan status", metro_values, default=metro_values, key="filter_metro"
    )
    sex_values = sorted(df["sex"].dropna().unique().tolist())
    selected_sex = st.sidebar.multiselect(
        "Sex", sex_values, default=sex_values, key="filter_sex"
    )
    selected_hours = st.sidebar.slider(
        "Arrival hour",
        min_value=0,
        max_value=23,
        value=(0, 23),
        help="Visits with missing arrival hour remain included when the full range is selected.",
        key="filter_hours",
    )

    hour_mask = df["arrival_hour"].between(selected_hours[0], selected_hours[1])
    if selected_hours == (0, 23):
        hour_mask = hour_mask | df["arrival_hour"].isna()

    return df[
        df["visit_month_name"].isin(selected_months)
        & df["visit_day"].isin(selected_days)
        & df["triage_level"].isin(selected_triage)
        & df["arrival_by_ambulance"].isin(selected_ambulance)
        & df["region"].isin(selected_regions)
        & df["metropolitan_status"].isin(selected_metro)
        & df["sex"].isin(selected_sex)
        & hour_mask
    ].copy()


def overview_page(df: pd.DataFrame) -> None:
    page_intro(
        "Executive overview",
        "Emergency Department Patient Flow",
        "A management-focused view of arrival demand, waiting performance, visit duration, and outcomes in the 2022 NHAMCS ED sample.",
    )
    st.markdown('<span class="status-chip">Unweighted public-use sample</span>', unsafe_allow_html=True)
    st.write("")
    kpi_cards(df)

    monthly = (
        df.groupby(["visit_month", "visit_month_name"], observed=True)
        .size()
        .reset_index(name="visits")
        .sort_values("visit_month")
    )
    hourly = df.dropna(subset=["arrival_hour"]).groupby("arrival_hour").size().reset_index(name="visits")

    left, right = st.columns(2)
    with left:
        st.subheader("Visit volume by month")
        chart = (
            alt.Chart(monthly)
            .mark_bar(color=TEAL, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("visit_month_name:N", sort=MONTH_ORDER, title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("visits:Q", title="Sample visits"),
                tooltip=[alt.Tooltip("visit_month_name:N", title="Month"), alt.Tooltip("visits:Q", format=",")],
            )
            .properties(height=310)
        )
        st.altair_chart(chart, width="stretch")
    with right:
        st.subheader("Visit volume by arrival hour")
        chart = (
            alt.Chart(hourly)
            .mark_line(color=BLUE, point=alt.OverlayMarkDef(color=BLUE, size=55), strokeWidth=3)
            .encode(
                x=alt.X("arrival_hour:Q", title="Hour of day", scale=alt.Scale(domain=[0, 23])),
                y=alt.Y("visits:Q", title="Sample visits", scale=alt.Scale(zero=True)),
                tooltip=[alt.Tooltip("arrival_hour:Q", title="Hour"), alt.Tooltip("visits:Q", format=",")],
            )
            .properties(height=310)
        )
        st.altair_chart(chart, width="stretch")

    busiest_month = monthly.loc[monthly["visits"].idxmax()] if not monthly.empty else None
    busiest_hour = hourly.loc[hourly["visits"].idxmax()] if not hourly.empty else None
    insights = st.columns(3)
    if busiest_month is not None:
        insights[0].markdown(
            f'<div class="insight-card"><strong>Highest-volume month</strong><p>{busiest_month["visit_month_name"]}: {int(busiest_month["visits"]):,} sampled visits.</p></div>',
            unsafe_allow_html=True,
        )
    if busiest_hour is not None:
        insights[1].markdown(
            f'<div class="insight-card"><strong>Highest-volume hour</strong><p>{int(busiest_hour["arrival_hour"]):02d}:00: {int(busiest_hour["visits"]):,} sampled visits.</p></div>',
            unsafe_allow_html=True,
        )
    insights[2].markdown(
        f'<div class="insight-card"><strong>Wait-time shape</strong><p>The mean wait is {df["wait_time_minutes"].mean():.1f} minutes versus a median of {df["wait_time_minutes"].median():.0f}, showing a right-skewed distribution.</p></div>',
        unsafe_allow_html=True,
    )


def patient_flow_page(df: pd.DataFrame) -> None:
    page_intro(
        "Demand patterns",
        "ED Patient Flow",
        "Explore when sampled ED visits arrive and how waiting and visit duration change across the day and week.",
    )
    day_summary = (
        df.groupby("visit_day", observed=True)
        .agg(
            visits=("visit_id", "count"),
            average_wait=("wait_time_minutes", "mean"),
            median_wait=("wait_time_minutes", "median"),
            average_visit_length=("visit_length_minutes", "mean"),
        )
        .reindex(DAY_ORDER)
        .dropna(how="all")
        .reset_index()
    )
    hour_summary = (
        df.dropna(subset=["arrival_hour"])
        .groupby("arrival_hour")
        .agg(visits=("visit_id", "count"), median_wait=("wait_time_minutes", "median"))
        .reset_index()
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Arrivals by day")
        day_chart = (
            alt.Chart(day_summary)
            .mark_bar(color=NAVY, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X("visit_day:N", sort=DAY_ORDER, title=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y("visits:Q", title="Sample visits"),
                tooltip=[alt.Tooltip("visit_day:N", title="Day"), alt.Tooltip("visits:Q", format=",")],
            )
            .properties(height=330)
        )
        st.altair_chart(day_chart, width="stretch")
    with right:
        st.subheader("Median wait by arrival hour")
        wait_chart = (
            alt.Chart(hour_summary)
            .mark_line(color=GOLD, point=True, strokeWidth=3)
            .encode(
                x=alt.X("arrival_hour:Q", title="Hour of day", scale=alt.Scale(domain=[0, 23])),
                y=alt.Y("median_wait:Q", title="Median wait (minutes)", scale=alt.Scale(zero=True)),
                tooltip=[
                    alt.Tooltip("arrival_hour:Q", title="Hour"),
                    alt.Tooltip("median_wait:Q", title="Median wait", format=".1f"),
                    alt.Tooltip("visits:Q", title="Visits", format=","),
                ],
            )
            .properties(height=330)
        )
        st.altair_chart(wait_chart, width="stretch")

    st.subheader("Day-level operating summary")
    display = day_summary.rename(
        columns={
            "visit_day": "Arrival day",
            "visits": "Visits",
            "average_wait": "Average wait (min)",
            "median_wait": "Median wait (min)",
            "average_visit_length": "Average visit length (min)",
        }
    )
    st.dataframe(display.round(1), hide_index=True, width="stretch")


def waiting_time_page(df: pd.DataFrame) -> None:
    page_intro(
        "Performance",
        "Waiting Time Analysis",
        "Compare the full wait-time distribution, operational thresholds, and variation between patient and location groups.",
    )
    kpi_cards(df)
    valid_waits = df.dropna(subset=["wait_time_minutes"]).copy()
    chart_waits = valid_waits[valid_waits["wait_time_minutes"] <= 360]

    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Wait-time distribution")
        histogram = (
            alt.Chart(chart_waits)
            .mark_bar(color=TEAL)
            .encode(
                x=alt.X(
                    "wait_time_minutes:Q",
                    bin=alt.Bin(step=15, extent=[0, 360]),
                    title="Wait time (minutes, displayed to 360)",
                ),
                y=alt.Y("count():Q", title="Sample visits"),
                tooltip=[alt.Tooltip("count():Q", title="Visits", format=",")],
            )
            .properties(height=330)
        )
        rules = alt.Chart(pd.DataFrame({"threshold": [120, 240], "label": ["2-hour", "4-hour"]})).mark_rule(
            strokeDash=[6, 4], strokeWidth=2
        ).encode(x="threshold:Q", color=alt.Color("label:N", scale=alt.Scale(range=[GOLD, RED]), title="Threshold"))
        st.altair_chart(histogram + rules, width="stretch")
        excluded = int((valid_waits["wait_time_minutes"] > 360).sum())
        st.caption(f"{excluded:,} valid waits above 360 minutes are retained in KPIs but omitted from this chart for readability.")
    with right:
        st.subheader("Median wait by triage level")
        triage_wait = (
            valid_waits.groupby("triage_level", observed=True)["wait_time_minutes"]
            .median()
            .reset_index(name="median_wait")
            .sort_values("median_wait", ascending=False)
        )
        chart = (
            alt.Chart(triage_wait)
            .mark_bar(color=NAVY, cornerRadiusEnd=3)
            .encode(
                y=alt.Y("triage_level:N", sort="-x", title=None),
                x=alt.X("median_wait:Q", title="Median wait (minutes)"),
                tooltip=[
                    alt.Tooltip("triage_level:N", title="Triage"),
                    alt.Tooltip("median_wait:Q", title="Median wait", format=".1f"),
                ],
            )
            .properties(height=330)
        )
        st.altair_chart(chart, width="stretch")

    comparison_options = {
        "Region": "region",
        "Metropolitan status": "metropolitan_status",
        "Sex": "sex",
        "Age group": "age_group",
        "Ambulance arrival": "arrival_by_ambulance",
        "Arrival period": "arrival_period",
    }
    selected_label = st.selectbox("Compare median wait by", list(comparison_options))
    selected_column = comparison_options[selected_label]
    comparison = (
        valid_waits.groupby(selected_column, observed=True)["wait_time_minutes"]
        .agg(valid_waits="count", average_wait="mean", median_wait="median")
        .reset_index()
        .sort_values("median_wait", ascending=False)
    )
    chart = (
        alt.Chart(comparison)
        .mark_bar(color=BLUE, cornerRadiusEnd=3)
        .encode(
            y=alt.Y(f"{selected_column}:N", sort="-x", title=None),
            x=alt.X("median_wait:Q", title="Median wait (minutes)"),
            tooltip=[
                alt.Tooltip(f"{selected_column}:N", title=selected_label),
                alt.Tooltip("valid_waits:Q", title="Valid waits", format=","),
                alt.Tooltip("average_wait:Q", title="Average wait", format=".1f"),
                alt.Tooltip("median_wait:Q", title="Median wait", format=".1f"),
            ],
        )
        .properties(height=max(220, 42 * len(comparison)))
    )
    st.altair_chart(chart, width="stretch")


def triage_page(df: pd.DataFrame) -> None:
    page_intro(
        "Acuity",
        "Triage and Patient Groups",
        "Review visit volume, waiting, admission, and visit duration across recorded triage categories.",
    )
    triage_summary = (
        df.groupby("triage_level", observed=True)
        .agg(
            visits=("visit_id", "count"),
            valid_waits=("wait_time_minutes", "count"),
            average_wait=("wait_time_minutes", "mean"),
            median_wait=("wait_time_minutes", "median"),
            average_visit_length=("visit_length_minutes", "mean"),
            admissions=("admitted_to_hospital", lambda values: int(values.eq("Yes").sum())),
        )
        .reset_index()
    )
    triage_summary["admission_rate"] = triage_summary["admissions"] / triage_summary["visits"] * 100
    triage_summary["triage_level"] = pd.Categorical(
        triage_summary["triage_level"], categories=TRIAGE_ORDER, ordered=True
    )
    triage_summary = triage_summary.sort_values("triage_level")

    left, right = st.columns(2)
    with left:
        st.subheader("Visits by triage level")
        chart = (
            alt.Chart(triage_summary)
            .mark_bar(color=TEAL, cornerRadiusEnd=3)
            .encode(
                y=alt.Y("triage_level:N", sort=TRIAGE_ORDER, title=None),
                x=alt.X("visits:Q", title="Sample visits"),
                tooltip=[alt.Tooltip("triage_level:N", title="Triage"), alt.Tooltip("visits:Q", format=",")],
            )
            .properties(height=360)
        )
        st.altair_chart(chart, width="stretch")
    with right:
        st.subheader("Admission rate by triage level")
        chart = (
            alt.Chart(triage_summary)
            .mark_bar(color=GOLD, cornerRadiusEnd=3)
            .encode(
                y=alt.Y("triage_level:N", sort=TRIAGE_ORDER, title=None),
                x=alt.X("admission_rate:Q", title="Admission rate (%)"),
                tooltip=[
                    alt.Tooltip("triage_level:N", title="Triage"),
                    alt.Tooltip("admission_rate:Q", title="Admission rate", format=".2f"),
                ],
            )
            .properties(height=360)
        )
        st.altair_chart(chart, width="stretch")

    display = triage_summary.rename(
        columns={
            "triage_level": "Triage level",
            "visits": "Visits",
            "valid_waits": "Valid waits",
            "average_wait": "Average wait (min)",
            "median_wait": "Median wait (min)",
            "average_visit_length": "Average visit length (min)",
            "admission_rate": "Admission rate (%)",
        }
    ).drop(columns="admissions")
    st.dataframe(display.round(2), hide_index=True, width="stretch")
    st.info(
        "Triage categories include unknown and non-standard classifications. Differences are descriptive and should not be interpreted as causal effects."
    )


def outcomes_page(df: pd.DataFrame) -> None:
    page_intro(
        "Disposition",
        "ED Outcomes",
        "Summarise hospital admission, observation, and leaving-before-care outcomes in the filtered sample.",
    )
    outcome_map = {
        "Admitted to hospital": "admitted_to_hospital",
        "Observation then hospitalized": "observation_then_hospitalized",
        "Observation then discharged": "observation_then_discharged",
        "Left without being seen": "left_without_being_seen",
        "Left before treatment complete": "left_before_treatment_complete",
        "Left against medical advice": "left_against_medical_advice",
        "Died in ED": "died_in_ed",
    }
    outcomes = pd.DataFrame(
        [
            {
                "outcome": label,
                "cases": int(df[column].eq("Yes").sum()),
                "rate": yes_rate(df[column]),
            }
            for label, column in outcome_map.items()
        ]
    ).sort_values("rate", ascending=False)

    top = st.columns(3)
    top[0].metric("Admissions", f"{int(df['admitted_to_hospital'].eq('Yes').sum()):,}")
    top[1].metric("Median visit length", f"{df['visit_length_minutes'].median():.0f} min")
    top[2].metric("Left without being seen", format_percentage(yes_rate(df["left_without_being_seen"])))

    bars = (
        alt.Chart(outcomes)
        .mark_bar(color=TEAL, cornerRadiusEnd=3)
        .encode(
            y=alt.Y("outcome:N", sort="-x", title=None),
            x=alt.X("rate:Q", title="Share of sampled visits (%)"),
            tooltip=[
                alt.Tooltip("outcome:N", title="Outcome"),
                alt.Tooltip("cases:Q", title="Cases", format=","),
                alt.Tooltip("rate:Q", title="Rate", format=".2f"),
            ],
        )
        .properties(height=360)
    )
    labels = bars.mark_text(align="left", baseline="middle", dx=4, color=NAVY).encode(
        text=alt.Text("rate:Q", format=".2f")
    )
    st.altair_chart(bars + labels, width="stretch")
    st.caption("Outcome fields are used for reporting only and are excluded from arrival-time prediction features.")


def sql_insights_page(df: pd.DataFrame) -> None:
    page_intro(
        "Reproducibility",
        "Data and SQL Layer",
        "The public dashboard reads the committed clean CSV for portable deployment. The MySQL scripts reproduce the staging, typed table, KPI, and analytical-view layers.",
    )
    steps = st.columns(4)
    step_content = [
        ("1. Prepare", "Select 39 ED-flow variables and standardise CDC missing codes."),
        ("2. Stage", "Load the clean CSV into a flexible MySQL staging table."),
        ("3. Type", "Cast validated fields into the final ed_visits table."),
        ("4. Analyse", "Use consistent KPI queries and reusable reporting views."),
    ]
    for column, (title, body) in zip(steps, step_content):
        column.markdown(
            f'<div class="method-step"><strong>{title}</strong><p>{body}</p></div>',
            unsafe_allow_html=True,
        )

    st.subheader("Current validation totals")
    validation = pd.DataFrame(
        {
            "Check": [
                "Total rows",
                "Unique visit IDs",
                "Valid wait records",
                "Missing wait records",
                "2-hour extended waits",
                "4-hour long waits",
            ],
            "Result": [
                len(df),
                df["visit_id"].nunique(),
                int(df["wait_time_minutes"].notna().sum()),
                int(df["wait_time_minutes"].isna().sum()),
                int(df["extended_wait_2hr_flag"].sum(skipna=True)),
                int(df["long_wait_4hr_flag"].sum(skipna=True)),
            ],
        }
    )
    st.dataframe(validation, hide_index=True, width="stretch")

    st.subheader("Reusable SQL views")
    view_map = pd.DataFrame(
        [
            ("vw_ed_patient_flow_summary", "Executive KPIs"),
            ("vw_ed_wait_kpis", "Wait coverage and threshold rates"),
            ("vw_ed_triage_flow", "Triage-level flow"),
            ("vw_ed_outcomes", "Admission and departure outcomes"),
            ("vw_ambulance_summary", "Arrival-mode comparison"),
            ("vw_region_summary", "Regional comparison"),
            ("vw_monthly_summary", "Monthly flow"),
            ("vw_day_summary", "Day-of-week flow"),
            ("vw_arrival_hour_summary", "Hourly flow"),
            ("vw_ml_wait_features", "Leakage-controlled model input"),
        ],
        columns=["SQL view", "Purpose"],
    )
    st.dataframe(view_map, hide_index=True, width="stretch")


def ml_page(filtered_df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    page_intro(
        "Analytical prototype",
        "Extended-Wait Prediction",
        "Compare leakage-controlled classifiers for the 2-hour extended-wait target. This model is for analysis and portfolio demonstration, not clinical decision-making.",
    )
    metrics = load_model_metrics()
    balance = load_target_balance()
    if metrics.empty:
        st.error(
            "Final model metrics are not available. Run `python src/train_wait_prediction_models.py` and refresh this page."
        )
        return

    best = metrics.sort_values(["f1", "roc_auc"], ascending=False).iloc[0]
    cards = st.columns(4)
    cards[0].metric("Selected model", str(best["model"]).replace("_", " ").title())
    cards[1].metric("ROC-AUC", f"{best['roc_auc']:.3f}")
    cards[2].metric("F1 score", f"{best['f1']:.3f}")
    cards[3].metric("Recall", f"{best['recall']:.3f}")

    st.subheader("Model comparison")
    display_columns = ["model", "accuracy", "precision", "recall", "f1", "roc_auc"]
    if "pr_auc" in metrics.columns:
        display_columns.append("pr_auc")
    display = metrics[display_columns].copy()
    display["model"] = display["model"].str.replace("_", " ").str.title()
    st.dataframe(display.round(3), hide_index=True, width="stretch")

    left, right = st.columns(2)
    with left:
        st.subheader("Target balance")
        if balance.empty:
            valid_waits = full_df["wait_time_minutes"].notna()
            balance = pd.DataFrame(
                {
                    "target": ["2-hour extended wait", "4-hour long wait"],
                    "positive_cases": [
                        int(full_df["extended_wait_2hr_flag"].sum(skipna=True)),
                        int(full_df["long_wait_4hr_flag"].sum(skipna=True)),
                    ],
                    "positive_rate_valid_waits": [
                        full_df.loc[valid_waits, "extended_wait_2hr_flag"].mean() * 100,
                        full_df.loc[valid_waits, "long_wait_4hr_flag"].mean() * 100,
                    ],
                }
            )
        st.dataframe(balance.round(3), hide_index=True, width="stretch")
    with right:
        st.subheader("Selected-model confusion counts")
        confusion = pd.DataFrame(
            {
                "Actual / predicted": [
                    "Actual no wait / predicted no wait",
                    "Actual no wait / predicted extended wait",
                    "Actual extended wait / predicted no wait",
                    "Actual extended wait / predicted extended wait",
                ],
                "Cases": [
                    int(best["true_negative"]),
                    int(best["false_positive"]),
                    int(best["false_negative"]),
                    int(best["true_positive"]),
                ],
            }
        )
        st.dataframe(confusion, hide_index=True, width="stretch")

    filtered_valid = filtered_df["wait_time_minutes"].notna()
    filtered_rate = filtered_df.loc[filtered_valid, "extended_wait_2hr_flag"].mean() * 100
    st.info(
        f"Within the current dashboard filters, {format_percentage(filtered_rate)} of visits with a valid wait meet the 2-hour target. "
        "Model performance above is from the fixed held-out test set and does not change with dashboard filters."
    )
    st.warning(
        "The best model has useful discrimination but limited precision. It should support analytical exploration only, not automated staffing, triage, or patient-level decisions."
    )


def recommendations_page(df: pd.DataFrame) -> None:
    page_intro(
        "Actionable interpretation",
        "Management Recommendations",
        "Recommendations are tied to descriptive patterns in the selected sample and should be validated against local operational data before implementation.",
    )
    recommendations = [
        (
            "Plan around recurring arrival peaks",
            "Use hour-, day-, and month-level demand profiles to review roster coverage and escalation readiness before predictable peaks.",
        ),
        (
            "Monitor both wait thresholds",
            "Use the 2-hour rate as an early pressure signal and the 4-hour rate as a stricter escalation indicator.",
        ),
        (
            "Segment operational reviews",
            "Compare wait performance by triage, ambulance arrival, region, and metropolitan status to identify where deeper local investigation is warranted.",
        ),
        (
            "Pair waits with downstream outcomes",
            "Review admission, observation, LWBS, and treatment-completion outcomes alongside wait KPIs instead of treating waiting time in isolation.",
        ),
    ]
    rows = [st.columns(2), st.columns(2)]
    for index, (title, body) in enumerate(recommendations):
        row, column = divmod(index, 2)
        rows[row][column].markdown(
            f'<div class="insight-card"><strong>{index + 1}. {title}</strong><p>{body}</p></div>',
            unsafe_allow_html=True,
        )

    st.subheader("Decision guardrails")
    guardrails = pd.DataFrame(
        [
            ("Use", "Descriptive KPI monitoring, portfolio demonstration, hypothesis generation"),
            ("Validate first", "Staffing changes, pathway redesign, comparisons with local hospitals"),
            ("Do not use", "Clinical triage, patient-level decisions, automated resource allocation"),
        ],
        columns=["Category", "Guidance"],
    )
    st.dataframe(guardrails, hide_index=True, width="stretch")
    st.caption(
        f"Current filtered sample: {len(df):,} visits. NHAMCS survey weights are retained in the data but this dashboard reports unweighted sample statistics."
    )


try:
    data = load_data()
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(f"The dashboard could not load its analytical data. {error}")
    st.info("Recreate the clean dataset with `python src/clean_nhamcs_csv.py`, then restart Streamlit.")
    st.stop()

st.sidebar.markdown("## ED Patient Flow")
st.sidebar.caption("2022 NHAMCS public-use sample")
page = st.sidebar.radio(
    "Dashboard section",
    [
        "Overview",
        "Patient Flow",
        "Waiting Times",
        "Triage & Groups",
        "Outcomes",
        "Data & SQL",
        "ML Evaluation",
        "Recommendations",
    ],
)
st.sidebar.divider()
filtered_data = apply_filters(data)
st.sidebar.caption(f"Showing {len(filtered_data):,} of {len(data):,} sampled visits")
if not filtered_data.empty:
    st.sidebar.download_button(
        "Download filtered data",
        data=filtered_data.to_csv(index=False).encode("utf-8"),
        file_name="filtered_ed_visits.csv",
        mime="text/csv",
        width="stretch",
    )

if filtered_data.empty:
    page_intro(
        "No matching records",
        "Adjust the dashboard filters",
        "The current combination of filters returns no sampled visits. Reset the filters or broaden one or more selections.",
    )
    st.stop()

if page == "Overview":
    overview_page(filtered_data)
elif page == "Patient Flow":
    patient_flow_page(filtered_data)
elif page == "Waiting Times":
    waiting_time_page(filtered_data)
elif page == "Triage & Groups":
    triage_page(filtered_data)
elif page == "Outcomes":
    outcomes_page(filtered_data)
elif page == "Data & SQL":
    sql_insights_page(filtered_data)
elif page == "ML Evaluation":
    ml_page(filtered_data, data)
else:
    recommendations_page(filtered_data)

st.markdown(
    """
    <div class="footer-note">
        Source: 2022 National Hospital Ambulatory Medical Care Survey Emergency Department Public Use File.
        Results are descriptive, unweighted sample statistics and are not clinical guidance.
    </div>
    """,
    unsafe_allow_html=True,
)

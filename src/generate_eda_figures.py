"""Regenerate the publication-ready EDA figures used by the repository."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "nhamcs_2022_visits_clean.csv"
FIGURE_DIR = PROJECT_ROOT / "outputs" / "figures"

NAVY = "#17324D"
TEAL = "#0F766E"
BLUE = "#2563EB"
GOLD = "#B7791F"
RED = "#B42318"
GRID = "#D9E2EC"
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TRIAGE_ORDER = ["Immediate", "Emergent", "Urgent", "Semi-urgent", "Nonurgent"]


def style_axis(axis, title: str, ylabel: str) -> None:
    axis.set_title(title, loc="left", fontsize=18, fontweight="semibold", color=NAVY, pad=18)
    axis.set_ylabel(ylabel, color=NAVY)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.grid(axis="y", color=GRID, linewidth=0.8)
    axis.set_axisbelow(True)
    axis.tick_params(colors="#475569")


def label_bars(axis) -> None:
    for container in axis.containers:
        axis.bar_label(container, fmt="{:,.0f}", padding=4, color=NAVY, fontsize=9)


def save(figure, name: str) -> None:
    figure.savefig(FIGURE_DIR / name, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH, na_values=["NULL", "", " "])
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

    monthly = (
        df.groupby(["visit_month", "visit_month_name"])
        .size()
        .reset_index(name="visits")
        .sort_values("visit_month")
    )
    figure, axis = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
    axis.bar(monthly["visit_month_name"].str[:3], monthly["visits"], color=TEAL)
    style_axis(axis, "ED Visits by Month", "Sample visits")
    axis.set_xlabel("Arrival month")
    label_bars(axis)
    save(figure, "ed_visits_by_month.png")

    daily = df.groupby("visit_day").size().reindex(DAY_ORDER)
    figure, axis = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
    axis.bar([day[:3] for day in DAY_ORDER], daily.values, color=BLUE)
    style_axis(axis, "ED Visits by Arrival Day", "Sample visits")
    axis.set_xlabel("Arrival day")
    label_bars(axis)
    save(figure, "ed_visits_by_day.png")

    hourly = df.groupby("arrival_hour").size().reindex(range(24), fill_value=0)
    figure, axis = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
    axis.bar(hourly.index.astype(int), hourly.values, color=NAVY)
    style_axis(axis, "ED Visits by Arrival Hour", "Sample visits")
    axis.set_xlabel("Hour of day")
    axis.set_xticks(range(24))
    label_bars(axis)
    save(figure, "ed_visits_by_hour.png")

    valid_waits = df["wait_time_minutes"].dropna()
    figure, axis = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
    axis.hist(valid_waits.clip(upper=360), bins=36, color=TEAL, edgecolor="white")
    axis.axvline(120, color=GOLD, linestyle="--", linewidth=2.2, label="2-hour threshold")
    axis.axvline(240, color=RED, linestyle="--", linewidth=2.2, label="4-hour threshold")
    style_axis(axis, "ED Wait-Time Distribution with Operational Thresholds", "Sample visits")
    axis.set_xlabel("Wait time in minutes (values above 360 capped for display)")
    axis.legend(frameon=False)
    save(figure, "wait_time_distribution_thresholds.png")

    triage = (
        df[df["triage_level"].isin(TRIAGE_ORDER)]
        .groupby("triage_level")["wait_time_minutes"]
        .median()
        .reindex(TRIAGE_ORDER)
    )
    figure, axis = plt.subplots(figsize=(11, 6.5), constrained_layout=True)
    axis.bar(triage.index, triage.values, color=GOLD)
    style_axis(axis, "Median Wait Time by Triage Level", "Median wait (minutes)")
    axis.set_xlabel("Triage level")
    label_bars(axis)
    save(figure, "median_wait_by_triage.png")

    print(f"Regenerated {5} figures in {FIGURE_DIR}")


if __name__ == "__main__":
    main()

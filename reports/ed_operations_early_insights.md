# ED Operations Early Insights

This report captures Python EDA findings for the NHAMCS 2022 Emergency Department patient flow project.

## Validation

- Python loads 16,025 ED visits and 39 selected fields from `data/processed/nhamcs_2022_visits_clean.csv`.
- `visit_id` has 0 duplicate values.
- `wait_time_minutes` is available for 13,272 visits and missing for 2,753 visits.
- The wait flags match the brief: 238 visits exceed 4 hours and 907 visits exceed 2 hours.

## Core Wait KPIs

- Average wait time: 36.0 minutes.
- Median wait time: 14.0 minutes.
- Average visit length: 298.6 minutes.
- Median visit length: 191.0 minutes.
- 2-hour extended-wait rate among valid waits: 6.83%.
- 4-hour long-wait rate among valid waits: 1.79%.

The 2-hour threshold should be the first ML target because it gives a less imbalanced target group than the 4-hour threshold. The 4-hour target remains useful as a stricter operational KPI.

## Volume Patterns

- Busiest month: February, with 1,619 visits.
- Busiest day: Monday, with 2,631 visits.
- Busiest arrival hour: 10:00, with 1,017 visits.

These patterns should be used to frame ED operational pressure around predictable demand peaks rather than department comparison.

## Wait-Time Variation

- Ambulance arrivals have a lower median wait than non-ambulance arrivals, which likely reflects urgency and triage priority.
- The Northeast and South show higher median waits than the Midwest and West in this sample.
- Metropolitan visits have a higher median wait than non-metropolitan visits.
- Children and patients aged 35-49 show slightly higher median waits than older groups in this early view.

These differences are descriptive and should be treated as operational signals for deeper analysis, not causal claims.

## Outcomes

- Admission rate: 13.24%.
- Observation then hospitalized rate: 1.10%.
- Observation then discharged rate: 1.34%.
- Left-without-being-seen rate: 2.04%.
- Left-before-treatment-complete rate: 1.38%.
- Ambulance-arrival rate: 17.77%.

Admission, observation, visit length, and leaving-before-care outcomes should support reporting and dashboard KPIs, but they must be excluded from arrival-time prediction features because they are only known after arrival.

## Dashboard Candidates

- KPI cards: total ED visits, median wait, average wait, 2-hour extended-wait rate, 4-hour long-wait rate, admission rate, left-without-being-seen rate, left-before-treatment-complete rate, and ambulance-arrival rate.
- Charts: visits by month, day, and arrival hour; wait-time distribution with 2-hour and 4-hour thresholds; median wait by triage level; median wait by region; outcome-rate summary.
- Filters: month, day, arrival hour or arrival period, triage level, ambulance arrival, age group, sex, region, and metropolitan status.

## Generated Figures

- `outputs/figures/ed_visits_by_month.png`
- `outputs/figures/ed_visits_by_day.png`
- `outputs/figures/ed_visits_by_hour.png`
- `outputs/figures/wait_time_distribution_thresholds.png`
- `outputs/figures/median_wait_by_triage.png`

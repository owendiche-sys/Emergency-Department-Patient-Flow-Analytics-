# Executive Summary

## Project Purpose

This project analyses Emergency Department patient flow using the 2022 NHAMCS Emergency Department public-use dataset. The goal is to identify operational pressure patterns, measure waiting-time and outcome KPIs, and provide practical recommendations for ED management.

The original broader hospital journey idea was narrowed to ED patient flow because the dataset represents ED visits and does not include a hospital department field.

## Key Dataset Facts

- 16,025 sampled ED visits.
- 13,272 visits with valid wait-time values.
- 907 visits waited more than 2 hours.
- 238 visits waited more than 4 hours.
- Each row represents one sampled ED visit, not a full inpatient journey.

## Early Findings

- Median ED wait time is 14 minutes.
- Average ED wait time is 36.0 minutes.
- The 2-hour extended-wait rate is 6.83% among visits with valid waits.
- The 4-hour long-wait rate is 1.79% among visits with valid waits.
- February has the highest visit volume in the current sample.
- Monday is the busiest arrival day.
- 10:00 is the busiest arrival hour.
- Ambulance arrivals have lower median waits than non-ambulance arrivals, which is consistent with triage prioritisation.
- Metropolitan visits and some regions show higher median waits, suggesting useful operational segmentation.

## Machine Learning Summary

The first modelling workflow predicts whether a visit is likely to exceed a 2-hour wait. The 2-hour flag is the primary ML target because it has more positive cases than the 4-hour flag and is less severely imbalanced.

The model uses arrival-time or near-arrival features only. Post-arrival outcomes such as admission status, visit length, observation outcomes, and leaving-before-care outcomes are excluded from the feature list.

## Dashboard Summary

The Streamlit dashboard currently includes:

- Overview
- ED Patient Flow
- Waiting Time Analysis
- Triage and Acuity
- Outcomes
- SQL Insights
- ML Prediction
- Business Recommendations

The dashboard uses the cleaned CSV for the current draft and is structured around the SQL views in `sql/05_views_for_python.sql`.

## Management Recommendations

- Use predictable arrival peaks to support staffing and operational readiness.
- Monitor 2-hour and 4-hour wait thresholds separately because they represent different pressure levels.
- Track wait variation by triage, ambulance arrival, region, and metropolitan status.
- Use admission, observation, and leaving-before-care outcomes for reporting, not arrival-time prediction.
- Treat the ML model as an analytical prototype, not a clinical or operational decision tool.

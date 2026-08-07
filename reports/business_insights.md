# Business Insights

## Business Question Mapping

| Business question | Current output |
|---|---|
| When are ED visits highest by month, day, and arrival hour? | Python EDA charts, dashboard patient-flow page, `vw_monthly_summary`, `vw_day_summary`, `vw_arrival_hour_summary` |
| What are the average and median ED wait times? | Python EDA summary, dashboard KPI cards, SQL KPI queries |
| What percentage of patients wait more than 2 or 4 hours? | Python EDA summary, dashboard KPI cards, `vw_ed_wait_kpis`, `vw_business_question_metrics` |
| Which triage levels and patient groups experience longer waits? | Python EDA charts, dashboard triage page, `vw_ed_triage_flow` |
| How do ambulance arrivals differ from non-ambulance arrivals? | Dashboard filters, `vw_ambulance_summary`, SQL KPI queries |
| What outcomes occur after ED visits? | Dashboard outcomes page, `vw_ed_outcomes`, SQL KPI queries |
| Which time periods show operational pressure? | Arrival-hour, day, and month summaries in Python/dashboard/SQL |
| Can arrival-time information predict extended waits? | Week 5 ML workflow and model metrics |

## Operational Insights

ED demand is not evenly distributed. Visit volume peaks by month, day, and hour, which means operational pressure can be framed around predictable demand patterns rather than unsupported department comparisons.

The 2-hour wait threshold is more useful for modelling because it has enough positive cases to support a first predictive workflow. The 4-hour wait threshold remains useful for executive reporting because it captures the most severe long waits.

Wait-time variation by triage level, ambulance arrival, region, and metropolitan status should be used as a practical management signal. These patterns are descriptive and should not be presented as causal findings.

Outcome measures such as admission, observation, left without being seen, and left before treatment complete are important for reporting and recommendations. They should not be used as arrival-time prediction features because they are only known after the patient journey has progressed.

## SQL View Use

The SQL phase includes core project-plan views and additional reusable summary views:

- `vw_ed_patient_flow_summary`
- `vw_ed_wait_kpis`
- `vw_ed_triage_flow`
- `vw_ed_outcomes`
- `vw_business_question_metrics`
- `vw_ml_wait_features`
- `vw_ambulance_summary`
- `vw_region_summary`
- `vw_monthly_summary`
- `vw_day_summary`
- `vw_arrival_hour_summary`

These views support cleaner dashboard and reporting logic by grouping recurring SQL outputs into reusable analytical layers.

## ML Interpretation

The model should be judged by precision, recall, F1-score, ROC-AUC, and confusion matrix counts, not accuracy alone. Because extended waits are uncommon, a high-accuracy model can still be weak if it mostly predicts the majority class.

For the first model comparison, logistic regression provides an interpretable baseline, while Random Forest gives a stronger nonlinear comparison point.

## Recommendations

- Add dashboard monitoring for arrival peaks by hour, day, and month.
- Use 2-hour waits as the operational early-warning target.
- Keep 4-hour waits as a stricter escalation KPI.
- Track outcome rates alongside wait metrics to show downstream pressure.
- Keep the ED-specific scope consistent across README, SQL, Python, dashboard, and reports.

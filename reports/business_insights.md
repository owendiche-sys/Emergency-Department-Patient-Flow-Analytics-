# Business Insights and Recommendations

## Business-question coverage

| Business question | Evidence |
|---|---|
| When are ED visits highest? | February was the highest-volume month, Monday the busiest arrival day, and 10:00 the busiest arrival hour. |
| What is waiting performance? | Average wait was 36.0 minutes and median wait was 14 minutes. |
| How often do extended waits occur? | 6.83% of valid waits were at least 2 hours; 1.79% exceeded 4 hours. |
| Which groups show longer waits? | Triage, ambulance arrival, age group, region, and metropolitan status show descriptive variation. |
| What outcomes occur? | Admission, observation, leaving-before-care, and ED death outcomes are summarised in SQL, Python, and the dashboard. |
| Can arrival information predict extended waits? | The balanced Random Forest reached ROC-AUC 0.715 and F1 0.246 on the fixed test set. |

## Demand and flow

Sampled arrivals are not distributed evenly across the year, week, or day. February recorded 1,619 sampled visits, Monday recorded 2,631, and 10:00 recorded 1,017. These are the clearest observed demand peaks in the prepared sample.

Management implication: use local arrival forecasts and roster data to test whether clinical, reception, diagnostic, and bed-management coverage is aligned with recurring demand peaks. NHAMCS describes a national sample of visits rather than the staffing requirements of a particular hospital, so it should guide questions rather than dictate staffing numbers.

## Waiting performance

The gap between the 36.0-minute average and 14-minute median shows that the wait distribution is strongly right-skewed. Most visits have relatively short waits, while a smaller group experiences substantially longer delays.

The project therefore reports two separate thresholds:

- `extended_wait_2hr_flag`: wait time of at least 120 minutes.
- `long_wait_4hr_flag`: wait time greater than 240 minutes.

The 2-hour rate is more sensitive to emerging pressure; the 4-hour rate isolates a smaller, more severe long-wait group. Both rates use the 13,272 visits with valid waiting times as their denominator.

## Triage and patient groups

Ambulance arrivals had a lower median wait than non-ambulance arrivals. Immediate and emergent triage categories also had shorter waits than several lower-acuity or non-standard triage groups. These patterns are consistent with urgency-based prioritisation but do not prove why individual waits differed.

The South and Northeast had higher descriptive median waits than the Midwest and West, and metropolitan visits had higher waits than non-metropolitan visits. These comparisons should be treated as signals for deeper review rather than league tables: the dashboard reports unweighted sampled visits and does not adjust for hospital mix, acuity, capacity, or survey design.

## Outcomes

Key outcome rates in the full sample were:

- Admission to hospital: 13.24%.
- Observation then hospitalised: 1.10%.
- Observation then discharged: 1.34%.
- Left without being seen: 2.04%.
- Left before treatment was complete: 1.38%.
- Ambulance arrival: 17.77%.

Management implication: monitor waiting measures with downstream outcomes. A stable median wait can conceal a rise in severe long waits or patients leaving before care is completed.

## Model interpretation

The predictive workflow uses arrival-time or near-arrival fields and excludes information learned only after the visit progresses. This prevents outcome leakage and keeps the model aligned with its stated use case.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Majority-class baseline | 0.932 | 0.000 | 0.000 | 0.000 | 0.500 |
| Balanced logistic regression | 0.615 | 0.097 | 0.558 | 0.165 | 0.628 |
| Balanced Random Forest | 0.794 | 0.164 | 0.492 | 0.246 | 0.715 |

The majority baseline demonstrates why accuracy alone is misleading: it achieves high accuracy while finding no extended waits. Random Forest offers better overall discrimination and F1, but its precision remains low. The model is suitable for analytical exploration, not automated triage or resource allocation.

## Recommended actions

1. Build local hourly and day-of-week arrival forecasts and compare them with actual roster coverage.
2. Place 2-hour and 4-hour rates on the same operational scorecard, always reporting the valid-wait denominator.
3. Review long-wait cases by triage and arrival mode to distinguish expected priority effects from process delays.
4. Monitor left-without-being-seen and treatment-completion outcomes alongside waits and admission flow.
5. Refit and validate the model with recent local operational data before considering any real-world use.

## Limitations

- Each row is a sampled ED visit, not a complete multi-department patient journey.
- Department comparison and readmission analysis are unsupported.
- Results are unweighted sample statistics and are not national estimates.
- Missing wait, triage, pain, and clinical measurements may influence comparisons.
- Observed associations are descriptive and do not establish causality.
- The model is an analytical prototype and not a clinical decision tool.

# Executive Summary

## Purpose

This project analyses emergency-department patient flow using the 2022 NHAMCS Emergency Department Public Use File. It combines SQL, Python, machine learning, and an interactive dashboard to identify arrival patterns, measure waiting and outcome KPIs, and translate descriptive evidence into management recommendations.

The scope is deliberately limited to an ED visit episode. The source data does not contain a hospital-department field or patient-level readmission tracking, so the project does not make department comparisons or readmission claims.

## Data foundation

The analytical dataset contains 16,025 sampled ED visits and 39 selected fields. Validation found:

- 16,025 unique visit IDs and no duplicate IDs.
- 13,272 visits with a valid wait time and 2,753 without one.
- 907 visits meeting the 2-hour extended-wait definition (`>= 120` minutes).
- 238 visits meeting the 4-hour long-wait definition (`> 240` minutes).

The dashboard and report present unweighted sample statistics. NHAMCS survey weights are retained but are not applied, so the results should not be interpreted as national population estimates.

## Principal findings

- Median wait was 14 minutes and average wait was 36.0 minutes, indicating a right-skewed distribution driven by a smaller group of long waits.
- The 2-hour extended-wait rate was 6.83% and the 4-hour long-wait rate was 1.79% among visits with a valid wait.
- Average visit length was 298.6 minutes and median visit length was 191 minutes.
- February had the highest sampled visit volume, Monday was the busiest arrival day, and 10:00 was the busiest arrival hour.
- Ambulance arrivals had a lower median wait than non-ambulance arrivals, consistent with urgency-based prioritisation.
- Metropolitan visits and the Northeast and South regions had higher descriptive median waits than their comparison groups in this sample.
- The admission rate was 13.24%, the left-without-being-seen rate was 2.04%, and the left-before-treatment-complete rate was 1.38%.

These patterns are descriptive. They identify areas for operational review but do not establish causal relationships.

## Model result

The model predicts whether a visit will meet the 2-hour extended-wait threshold using only arrival-time or near-arrival features. Post-arrival outcomes, raw wait time, visit duration, diagnoses, and procedures are excluded to prevent leakage.

The balanced Random Forest was the strongest tested classifier, with accuracy 0.794, precision 0.164, recall 0.492, F1 0.246, and ROC-AUC 0.715. It offers useful analytical discrimination, but limited precision makes it unsuitable for automated operational or clinical decisions.

## Recommendations

1. Use recurring arrival-hour, day, and month patterns to review roster coverage and escalation readiness before predictable peaks.
2. Track the 2-hour rate as an early pressure signal and the 4-hour rate as a stricter escalation indicator.
3. Segment operational reviews by triage, ambulance arrival, region, and metropolitan status to identify where local investigation is needed.
4. Review admission, observation, left-without-being-seen, and treatment-completion outcomes alongside waiting measures.
5. Validate all proposed operational changes against recent local hospital data before implementation.

## Final deliverable

The repository provides a reproducible SQL and Python workflow, validated analytical data, model evaluation, publication-ready figures, final reports, and a deployment-ready Streamlit dashboard. It is an analytical portfolio project and decision-support demonstration, not a clinical system.

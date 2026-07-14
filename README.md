# Emergency Department Patient Flow Analytics

## Project overview

This project uses the **2022 National Hospital Ambulatory Medical Care Survey (NHAMCS) Emergency Department Public Use File** to analyse ED visit patterns, waiting times, triage urgency, ambulance arrivals, admission outcomes, and patients leaving before care is completed.

The project was originally planned as a broader hospital patient journey analysis. After validating the selected dataset, the scope was narrowed to ED patient flow because each row represents one sampled emergency-department visit and the data does not include a hospital department field.

## Why Emergency Department?

Emergency departments are high-pressure entry points into hospital care. They manage unpredictable arrivals, urgent triage decisions, ambulance arrivals, long-wait risk, admission flow, and patients who may leave before care is completed.

The selected NHAMCS dataset directly supports this ED-focused analysis because it includes arrival timing, waiting time, triage level, ambulance arrival, visit length, admission outcomes, and departure-related indicators. It does **not** support comparing hospital departments, so this project does not make department-pressure claims.

## Problem statement

Emergency departments often experience operational pressure caused by fluctuating arrivals, long waits, triage demand, ambulance arrivals, admission bottlenecks, and patients leaving before care is completed. Without a clear analytics workflow, it can be difficult for hospital managers to identify peak pressure periods, understand which patient groups experience longer waits, and communicate evidence-based recommendations.

This project builds an ED patient flow analytics workflow that uses SQL, Python, machine learning, and dashboard reporting to monitor ED operational KPIs and support practical management recommendations.

## Project goals

- Measure ED patient volume, waiting times, visit length, admission outcomes, and departure patterns.
- Identify busy arrival periods and signs of ED operational pressure.
- Analyse how wait times vary by triage level, arrival period, ambulance arrival, age group, sex, region, and metropolitan status.
- Compare 2-hour and 4-hour wait thresholds.
- Predict extended patient waiting times using arrival-time or near-arrival features.
- Turn findings into practical recommendations for hospital management.

## Business questions

- When are ED visits highest by month, day, and arrival hour?
- What are the average and median ED wait times?
- What percentage of patients wait more than 2 hours or 4 hours?
- Which triage levels and patient groups experience longer waits?
- How do ambulance arrivals differ from non-ambulance arrivals?
- What proportion of ED visits result in admission, observation, discharge-related outcomes, or patients leaving before care is completed?
- Which time periods show the strongest signs of ED operational pressure?
- Can arrival-time information help predict whether a patient is at risk of an extended wait?

## Core KPIs

- Total ED visits
- Average and median wait time
- Average and median visit length
- 2-hour extended-wait rate
- 4-hour long-wait rate
- Admission rate
- Left-without-being-seen rate
- Left-before-treatment-complete rate
- Ambulance-arrival rate
- Visits by month, day, and arrival hour
- Wait time by triage level, arrival period, ambulance arrival, age group, sex, region, and metropolitan status

## Planned stack

- SQL for data modelling, cleaning, KPIs, and reusable views
- Python for exploratory analysis and visualisation
- scikit-learn for extended-wait prediction
- Streamlit for the final dashboard

## Repository structure

```text
data/
  raw/          # Original CDC Stata file (not committed)
  processed/    # SQL-ready selected ED visit data
notebooks/      # Exploratory analysis and machine-learning notebooks
sql/            # Database setup, cleaning, KPI, and view scripts
src/            # Reusable Python modules and generation scripts
dashboard/      # Streamlit application
reports/        # Executive summary and business insights
outputs/
  figures/      # Exported charts and dashboard screenshots
  models/       # Saved model artefacts
docs/           # Data dictionary, project plans, and supporting documentation
```

## Dataset

The selected dataset is the **2022 National Hospital Ambulatory Medical Care Survey (NHAMCS) Emergency Department Public Use File**, published by the US Centers for Disease Control and Prevention, National Center for Health Statistics.

- [CDC dataset and documentation page](https://www.cdc.gov/nchs/nhamcs/documentation/index.html)
- [2022 technical documentation (PDF)](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHAMCS/doc22-ed-508.pdf)
- Unit of observation: one sampled emergency-department visit
- Source data: 16,025 visits and 913 variables
- Prepared SQL handoff data: 16,025 visits and 39 selected variables
- Access date: 3 July 2026
- Privacy: public-use microdata with disclosure protections and no direct patient identifiers in the selected fields

The raw Stata file is retained locally and ignored by Git. The reproducible preparation script creates `data/processed/nhamcs_2022_visits.csv`, converts CDC special missing codes to blank values, decodes selected categories, and creates two wait-time flags.

The four-hour target is available, but only 238 of 13,272 visits with valid wait times exceed 240 minutes. A two-hour target is also supplied for comparison because it has a less extreme class imbalance.

## Scope limitations

- The dataset does not include a hospital department field, so the project does not compare departments.
- The project analyses an ED visit episode, not the full hospital journey across multiple departments.
- Readmission analysis is not included because the prepared dataset does not support it.
- The machine learning model is an analytical prototype, not a clinical or operational automation tool.
- Post-arrival outcomes such as admission status, visit length, and leaving-before-care outcomes should not be used as arrival-time prediction features.

## Team workflow

- `main` - stable shared work
- `feature/nimi` - SQL schema, cleaning, KPIs, and views
- `feature/owen` - Python analysis, ML, and dashboard work

## Contribution focus

- **Owen:** Python EDA, machine learning, model evaluation, Streamlit dashboard, visual analysis, and final analytics storytelling.
- **Nimi:** SQL database design, SQL loading and cleaning, KPI queries, reporting views, SQL documentation, and SQL-backed business questions.
- **Shared:** project scope, business questions, executive summary, business insights, final recommendations, and portfolio-ready documentation.

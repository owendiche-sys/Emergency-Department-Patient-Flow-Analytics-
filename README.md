# Hospital Patient Journey Analytics

Portfolio project analysing emergency-department patient flow with SQL, Python, machine learning, and a Streamlit dashboard.

## Project goals

- Measure patient volume, waiting times, admission and departure patterns.
- Identify busy arrival periods and high-pressure patient groups.
- Predict extended patient waiting times.
- Turn findings into practical recommendations for hospital management.

## Planned stack

- SQL for data modelling, cleaning, KPIs, and reusable views
- Python for exploratory analysis and visualisation
- scikit-learn for long-wait prediction
- Streamlit for the final dashboard

## Repository structure

```text
data/
  raw/          # Original CDC Stata file (not committed)
  processed/    # SQL-ready selected visit data
notebooks/      # Exploratory analysis and machine-learning notebooks
sql/            # Database setup, cleaning, KPI, and view scripts
src/            # Reusable Python modules
dashboard/      # Streamlit application
reports/        # Executive summary and business insights
outputs/
  figures/      # Exported charts and dashboard screenshots
  models/       # Saved model artefacts
docs/           # Data dictionary and supporting documentation
```

## Dataset

The selected dataset is the **2022 National Hospital Ambulatory Medical Care Survey (NHAMCS) Emergency Department Public Use File**, published by the US Centers for Disease Control and Prevention, National Center for Health Statistics.

- [CDC dataset and documentation page](https://www.cdc.gov/nchs/nhamcs/documentation/index.html)
- [2022 technical documentation (PDF)](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHAMCS/doc22-ed-508.pdf)
- Unit of observation: one sampled emergency-department visit
- Source data: 16,025 visits and 913 variables
- Prepared data: 16,025 visits and 38 selected variables

The raw Stata file is retained locally and ignored by Git. The reproducible preparation script creates `data/processed/nhamcs_2022_visits.csv`, converts CDC special missing codes to blank values, decodes selected categories, and creates two wait-time flags.

The planned four-hour target is available, but only 238 of 13,272 visits with valid wait times exceed 240 minutes. A two-hour target is also supplied for comparison because it has a less extreme class imbalance.

## Week 1 status (1–5 July 2026)

- [x] Create the local repository structure
- [x] Start the README
- [x] Select and document the final dataset
- [x] Confirm that the source is a CDC/NCHS public-use file
- [x] Audit columns, missing values, data types, and possible ML targets
- [x] Create the SQL-ready CSV and supporting documentation
- [ ] Create the GitHub repository and working branches
- [ ] Draft the SQL schema from the selected columns

## Team workflow

- `main` — stable shared work
- `owen` — Python analysis, ML, and dashboard work
- `nimi` — SQL schema, cleaning, KPIs, and views

Owen begins Python analysis from the prepared CSV while Nimi develops the SQL layer. Integration begins once the SQL views are ready.

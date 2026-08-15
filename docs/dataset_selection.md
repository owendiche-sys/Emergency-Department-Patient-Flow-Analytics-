# Dataset Selection Record

## Selected dataset

- **Dataset name:** 2022 NHAMCS Emergency Department Public Use File
- **Publisher:** US Centers for Disease Control and Prevention, National Center for Health Statistics
- **Source:** https://www.cdc.gov/nchs/nhamcs/documentation/index.html
- **Technical documentation:** https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHAMCS/doc22-ed-508.pdf
- **Access date:** 3 July 2026
- **Access status:** CDC/NCHS public-use file
- **Repository decision:** Retain the public-use source file and the selected, reproducibly prepared CSV with clear source attribution
- **Privacy:** Public-use microdata with disclosure protections; no direct patient identifiers in the selected fields

## Suitability checks

- [x] Each row represents one sampled emergency-department visit
- [x] Arrival time and waiting time are available
- [x] Triage/urgency is available
- [x] Admission and departure outcomes are available
- [x] Age is available, with the oldest ages grouped by the source
- [x] A four-hour wait flag can be created
- [x] No direct patient identifiers are present in the selected fields
- [ ] A hospital department field is available (not present in the public-use file)

## Decision

**Status:** Selected

NHAMCS provides genuine patient-level emergency-department visit data with measured waiting time, arrival time, triage urgency, demographics, initial vital signs, diagnoses, procedures, and disposition. It supports SQL KPI analysis, Python EDA, and long-wait prediction.

The dataset supports an **Emergency Department patient flow** project, not a general hospital department comparison project. Each row represents one sampled ED visit, so the valid project scope is ED operational performance: arrival patterns, waiting times, triage urgency, ambulance arrival, visit length, admission outcomes, and patients leaving before care is completed.

Its main limitations are the absence of a hospital department field, lack of readmission tracking, survey-specific missing-value codes, and strong imbalance in the four-hour wait target. Because no department field is available, the project should not include department tables, department counts, average wait by department, busiest departments, or a department pressure index. Those ideas should be replaced with ED operational pressure measures such as peak arrival periods, long-wait rates, triage-level patterns, ambulance-arrival patterns, admission outcomes, and left-without-being-seen rates.

The prepared SQL handoff table contains 16,025 rows and 39 fields. The additional `visit_month_name` field provides a readable month label while `visit_month` remains the sortable month number. See `nhamcs_2022_data_dictionary.csv` and `nhamcs_2022_data_quality_report.md` for details.

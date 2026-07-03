# Dataset Selection Record

## Selected dataset

- **Dataset name:** 2022 NHAMCS Emergency Department Public Use File
- **Publisher:** US Centers for Disease Control and Prevention, National Center for Health Statistics
- **Source:** https://www.cdc.gov/nchs/nhamcs/documentation/index.html
- **Technical documentation:** https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/NHAMCS/doc22-ed-508.pdf
- **Access date:** 3 July 2026
- **Access status:** CDC/NCHS public-use file
- **GitHub decision:** Keep the original Stata file out of Git; commit the selected, reproducibly prepared CSV with source attribution
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

Its main limitations are the absence of a department field, survey-specific missing-value codes, and strong imbalance in the four-hour wait target. The prepared handoff table contains 16,025 rows and 38 fields. See `nhamcs_2022_data_dictionary.csv` and `nhamcs_2022_data_quality_report.md` for details.

USE ed_patient_flow_analytics;

/*==============================================================
  04_KPI_QUERIES.SQL
  Project: Emergency Department Patient Flow Analytics

  Purpose:
  Business KPI queries used during Exploratory Data Analysis (EDA).

  Author: Adeniyi Tijesunimi
==============================================================*/

/*====================================================================
SECTION 1 — WAIT TIME ANALYSIS
======================================================================

Business Questions
------------------
1. What is the average ED waiting time?
2. What is the median waiting time?
3. What are the minimum and maximum waiting times?
4. What is the variability in waiting times?
5. How are waiting times distributed?
6. How many patients waited over 2 hours?
7. How many patients waited over 4 hours?
8. Which patients experienced the longest waits?

*/


-- Query 1
-- Average waiting time

SELECT
    ROUND(AVG(wait_time_minutes),2) AS average_wait
FROM ed_visits;


-- Query 2
-- Median waiting time

SELECT ROUND(AVG(wait_time_minutes), 2) AS median_wait
FROM (
    SELECT
        wait_time_minutes,
        ROW_NUMBER() OVER (ORDER BY wait_time_minutes) AS row_num,
        COUNT(*) OVER () AS row_count
    FROM ed_visits
    WHERE wait_time_minutes IS NOT NULL
) AS ranked_waits
WHERE row_num IN (
    FLOOR((row_count + 1) / 2),
    FLOOR((row_count + 2) / 2)
);


-- Query 3
-- Minimum and maximum waiting time

SELECT
    MIN(wait_time_minutes) AS min_wait,
    MAX(wait_time_minutes) AS max_wait,
    ROUND(AVG(wait_time_minutes),2) AS avg_wait
FROM ed_visits;


-- Query 4
-- Standard deviation of waiting time

SELECT
    ROUND(STDDEV(wait_time_minutes),2) AS wait_time_std_dev
FROM ed_visits;


-- Query 5
-- Waiting time distribution

SELECT
CASE
    WHEN wait_time_minutes IS NULL THEN 'Missing'
    WHEN wait_time_minutes < 30 THEN 'Under 30 mins'
    WHEN wait_time_minutes < 60 THEN '30-59 mins'
    WHEN wait_time_minutes < 120 THEN '60-119 mins'
    WHEN wait_time_minutes <= 240 THEN '120-240 mins'
    ELSE 'Over 240 mins'
END AS wait_category,
COUNT(*) AS patients
FROM ed_visits
GROUP BY wait_category
ORDER BY
CASE wait_category
    WHEN 'Under 30 mins' THEN 1
    WHEN '30-59 mins' THEN 2
    WHEN '60-119 mins' THEN 3
    WHEN '120-240 mins' THEN 4
    WHEN 'Over 240 mins' THEN 5
    WHEN 'Missing' THEN 6
END;


-- Query 6
-- Patients waiting over 2 hours

SELECT
    COUNT(*) AS patients_over_2hrs,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM ed_visits WHERE wait_time_minutes IS NOT NULL),
        2
    ) AS percentage
FROM ed_visits
WHERE wait_time_minutes >= 120;


-- Query 7
-- Patients waiting over 4 hours

SELECT
    COUNT(*) AS patients_over_4hrs,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM ed_visits WHERE wait_time_minutes IS NOT NULL),
        2
    ) AS percentage
FROM ed_visits
WHERE wait_time_minutes > 240;


-- Query 8
-- Top 20 longest waits

SELECT
    visit_id,
    wait_time_minutes
FROM ed_visits
ORDER BY wait_time_minutes DESC
LIMIT 20;


/*====================================================================
SECTION 2 — VISIT LENGTH ANALYSIS
======================================================================

Business Questions
------------------
1. What is the average ED visit length?
2. What is the median visit length?
3. What are the shortest and longest visits?
4. How are visit durations distributed?
5. How variable are visit durations?
6. Do admitted patients stay longer?
7. Which admission destinations have the longest stays?

*/


-- Query 1
-- Average visit length

SELECT
    ROUND(AVG(visit_length_minutes),2) AS average_visit_length
FROM ed_visits;


-- Query 2
-- Median visit length

SELECT ROUND(AVG(visit_length_minutes), 2) AS median_visit_length
FROM (
    SELECT
        visit_length_minutes,
        ROW_NUMBER() OVER (ORDER BY visit_length_minutes) AS row_num,
        COUNT(*) OVER () AS row_count
    FROM ed_visits
    WHERE visit_length_minutes IS NOT NULL
) AS ranked_visits
WHERE row_num IN (
    FLOOR((row_count + 1) / 2),
    FLOOR((row_count + 2) / 2)
);


-- Query 3
-- Shortest and longest visits

SELECT
    MIN(visit_length_minutes) AS shortest_visit,
    MAX(visit_length_minutes) AS longest_visit
FROM ed_visits;


-- Query 4
-- Visit duration categories

SELECT
CASE
    WHEN visit_length_minutes < 120 THEN 'Under 2 hours'
    WHEN visit_length_minutes < 240 THEN '2–4 hours'
    WHEN visit_length_minutes < 480 THEN '4–8 hours'
    WHEN visit_length_minutes < 720 THEN '8–12 hours'
    ELSE 'Over 12 hours'
END AS visit_duration,
COUNT(*) AS patients
FROM ed_visits
GROUP BY visit_duration
ORDER BY
CASE visit_duration
    WHEN 'Under 2 hours' THEN 1
    WHEN '2–4 hours' THEN 2
    WHEN '4–8 hours' THEN 3
    WHEN '8–12 hours' THEN 4
    WHEN 'Over 12 hours' THEN 5
END;


-- Query 5
-- Standard deviation of visit length

SELECT
    ROUND(STDDEV(visit_length_minutes),2) AS visit_length_std_dev
FROM ed_visits;


-- Query 6
-- Visit length by admission status

SELECT
    admitted_to_hospital,
    ROUND(AVG(visit_length_minutes),2) AS average_visit_length,
    COUNT(*) AS patients
FROM ed_visits
GROUP BY admitted_to_hospital;


-- Query 7
-- Visit length by admission destination

SELECT
    admission_destination,
    ROUND(AVG(visit_length_minutes),2) AS average_visit_length,
    COUNT(*) AS patients
FROM ed_visits
WHERE admission_destination IS NOT NULL
GROUP BY admission_destination
ORDER BY average_visit_length DESC;


/*====================================================================
SECTION 3 — PATIENT DEMOGRAPHICS
======================================================================

Business Questions
------------------
1. What is the age distribution of ED patients?
2. What is the average patient age?
3. What is the gender distribution?
4. What is the residence type distribution?

*/


-- Query 1
-- Patient age groups

SELECT
CASE
    WHEN age_years < 18 THEN 'Children (<18)'
    WHEN age_years < 40 THEN 'Young Adults (18–39)'
    WHEN age_years < 65 THEN 'Adults (40–64)'
    ELSE 'Older Adults (65+)'
END AS age_group,
COUNT(*) AS patients
FROM ed_visits
GROUP BY age_group
ORDER BY
CASE age_group
    WHEN 'Children (<18)' THEN 1
    WHEN 'Young Adults (18–39)' THEN 2
    WHEN 'Adults (40–64)' THEN 3
    WHEN 'Older Adults (65+)' THEN 4
END;


-- Query 2
-- Age summary statistics

SELECT
ROUND(AVG(age_years),2) AS average_age,
MIN(age_years) AS youngest_patient,
MAX(age_years) AS oldest_patient
FROM ed_visits;


-- Query 3
-- Sex distribution

SELECT
sex,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY sex
ORDER BY patients DESC;


-- Query 4
-- Residence type distribution

SELECT
residence_type,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY residence_type
ORDER BY patients DESC;


/*====================================================================
SECTION 4 — TRIAGE & ACUITY ANALYSIS
======================================================================

Business Questions
------------------
1. What is the distribution of triage levels?
2. How are patients distributed by acuity group?
3. Which triage levels wait the longest?
4. Which triage levels stay the longest?
5. Which triage levels have the highest admission rates?

*/


-- Query 1
-- Distribution of triage levels

SELECT
triage_level,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY triage_level
ORDER BY patients DESC;


-- Query 2
-- Distribution by acuity group

SELECT
CASE
    WHEN triage_level IN ('Immediate','Emergent')
        THEN 'High Acuity'
    WHEN triage_level='Urgent'
        THEN 'Moderate Acuity'
    WHEN triage_level IN ('Semi-urgent','Nonurgent')
        THEN 'Low Acuity'
    ELSE 'Unknown / No Triage'
END AS acuity_group,

COUNT(*) AS patients,

ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage

FROM ed_visits

GROUP BY acuity_group;


-- Query 3
-- Average waiting time by triage level

SELECT
triage_level,
ROUND(AVG(wait_time_minutes),2) AS average_wait,
COUNT(*) AS patients
FROM ed_visits
GROUP BY triage_level
ORDER BY average_wait;


-- Query 4
-- Average visit length by triage level

SELECT
triage_level,
ROUND(AVG(visit_length_minutes),2) AS average_visit_length,
COUNT(*) AS patients
FROM ed_visits
GROUP BY triage_level
ORDER BY average_visit_length DESC;


-- Query 5
-- Admission rate by triage level

SELECT
triage_level,
COUNT(*) AS total_patients,
SUM(admitted_to_hospital='Yes') AS admitted,

ROUND(
SUM(admitted_to_hospital='Yes')*100.0/
COUNT(*),
2
) AS admission_rate

FROM ed_visits

GROUP BY triage_level

ORDER BY admission_rate DESC;


/*====================================================================
SECTION 5 — AMBULANCE ARRIVALS
======================================================================

Business Questions
------------------
1. What percentage of patients arrive by ambulance?
2. What percentage of ambulance patients are transferred?
3. Do ambulance patients wait longer?
4. Do ambulance patients stay longer?
5. Are ambulance patients more likely to be admitted?
6. What triage levels are most common among ambulance arrivals?
7. What percentage of all hospital admissions arrived by ambulance?

*/


-- Query 1
-- Arrival by ambulance distribution

SELECT
arrival_by_ambulance,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY arrival_by_ambulance;


-- Query 2
-- Ambulance transfer distribution (ambulance arrivals only)

SELECT
ambulance_transfer,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(
SELECT COUNT(*)
FROM ed_visits
WHERE arrival_by_ambulance='Yes'
),
2
) AS percentage
FROM ed_visits
WHERE arrival_by_ambulance='Yes'
GROUP BY ambulance_transfer;


-- Query 3
-- Average wait time by ambulance arrival

SELECT
arrival_by_ambulance,
ROUND(AVG(wait_time_minutes),2) AS average_wait,
COUNT(*) AS patients
FROM ed_visits
GROUP BY arrival_by_ambulance;


-- Query 4
-- Average visit length by ambulance arrival

SELECT
arrival_by_ambulance,
ROUND(AVG(visit_length_minutes),2) AS average_visit_length,
COUNT(*) AS patients
FROM ed_visits
GROUP BY arrival_by_ambulance;


-- Query 5
-- Admission rate by ambulance arrival

SELECT
arrival_by_ambulance,
COUNT(*) AS total_patients,
SUM(admitted_to_hospital='Yes') AS admitted,

ROUND(
SUM(admitted_to_hospital='Yes')*100.0/
COUNT(*),
2
) AS admission_rate

FROM ed_visits

GROUP BY arrival_by_ambulance;


-- Query 6
-- Triage level by ambulance arrival

SELECT
arrival_by_ambulance,
triage_level,
COUNT(*) AS patients
FROM ed_visits
GROUP BY arrival_by_ambulance, triage_level
ORDER BY arrival_by_ambulance, patients DESC;


-- Query 7
-- Percentage of admitted patients arriving by ambulance

SELECT
arrival_by_ambulance,
COUNT(*) AS admitted_patients,

ROUND(
COUNT(*)*100.0/
(
SELECT COUNT(*)
FROM ed_visits
WHERE admitted_to_hospital='Yes'
),
2
) AS percentage_of_all_admissions

FROM ed_visits

WHERE admitted_to_hospital='Yes'

GROUP BY arrival_by_ambulance;


/*====================================================================
SECTION 6 — ADMISSION OUTCOMES
======================================================================

Business Questions
------------------
1. How many patients were admitted?
2. How many were discharged after observation?
3. How many were hospitalized after observation?
4. How many left without being seen?
5. How many left before treatment was complete?
6. How many left against medical advice?
7. How many died in the ED?
8. Where were admitted patients sent?

*/


-- Query 1
-- Hospital admission status

SELECT
admitted_to_hospital,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY admitted_to_hospital;


-- Query 2
-- Observation then discharged

SELECT
observation_then_discharged,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY observation_then_discharged;


-- Query 3
-- Observation then hospitalized

SELECT
observation_then_hospitalized,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY observation_then_hospitalized;


-- Query 4
-- Left without being seen

SELECT
left_without_being_seen,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY left_without_being_seen;


-- Query 5
-- Left before treatment complete

SELECT
left_before_treatment_complete,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY left_before_treatment_complete;


-- Query 6
-- Left against medical advice

SELECT
left_against_medical_advice,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY left_against_medical_advice;


-- Query 7
-- Deaths in ED

SELECT
died_in_ed,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY died_in_ed;


-- Query 8
-- Admission destination distribution

SELECT
admission_destination,
COUNT(*) AS patients,
ROUND(
COUNT(*)*100.0/
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage
FROM ed_visits
GROUP BY admission_destination
ORDER BY patients DESC;


/*====================================================================
SECTION 7 — GEOGRAPHIC ANALYSIS
======================================================================

Business Questions
------------------
1. Which region has the highest visit volume?
2. Which region has the longest average wait time?
3. Which region has the highest admission rate?

*/


-- Query 1
-- Visit volume by region

SELECT
region,
COUNT(*) AS visits,

ROUND(
COUNT(*) * 100.0 /
(SELECT COUNT(*) FROM ed_visits),
2
) AS percentage

FROM ed_visits

GROUP BY region

ORDER BY visits DESC;


-- Query 2
-- Average waiting time by region

SELECT
region,
ROUND(AVG(wait_time_minutes),2) AS avg_wait_minutes,
COUNT(*) AS visits

FROM ed_visits

GROUP BY region

ORDER BY avg_wait_minutes DESC;


-- Query 3
-- Admission rate by region

SELECT
region,
COUNT(*) AS visits,

SUM(admitted_to_hospital='Yes') AS admitted,

ROUND(
SUM(admitted_to_hospital='Yes')*100.0/
COUNT(*),
2
) AS admission_rate

FROM ed_visits

GROUP BY region

ORDER BY admission_rate DESC;


/*====================================================================
SECTION 8 — PEAK ARRIVAL PATTERNS
======================================================================

Business Questions
------------------
1. Which hour has the highest patient arrivals?
2. Which day receives the most visits?
3. Which month records the highest patient volume?
4. Which arrival hour has the longest average wait?
5. Which weekday has the longest average wait?
6. Which month has the longest average wait?
7. Which arrival hour creates the greatest workload?
8. Which arrival hour has the highest admission rate?

*/


-- Query 1
-- Visits by arrival hour

SELECT
arrival_hour,
COUNT(*) AS visits

FROM ed_visits

GROUP BY arrival_hour

ORDER BY arrival_hour;


-- Query 2
-- Visits by weekday

SELECT
visit_day,
COUNT(*) AS visits

FROM ed_visits

GROUP BY visit_day

ORDER BY visits DESC;


-- Query 3
-- Visits by month

SELECT
visit_month,
visit_month_name,
COUNT(*) AS visits

FROM ed_visits

GROUP BY visit_month, visit_month_name

ORDER BY visit_month;


-- Query 4
-- Average wait by arrival hour

SELECT
arrival_hour,
ROUND(AVG(wait_time_minutes),2) AS avg_wait,
COUNT(*) AS visits

FROM ed_visits

GROUP BY arrival_hour

ORDER BY arrival_hour;


-- Query 5
-- Average wait by weekday

SELECT
visit_day,
ROUND(AVG(wait_time_minutes),2) AS avg_wait,
COUNT(*) AS visits

FROM ed_visits

GROUP BY visit_day

ORDER BY avg_wait DESC;


-- Query 6
-- Average wait by month

SELECT
visit_month,
visit_month_name,
ROUND(AVG(wait_time_minutes),2) AS avg_wait,
COUNT(*) AS visits

FROM ed_visits

GROUP BY visit_month, visit_month_name

ORDER BY visit_month;


-- Query 7
-- Operational workload index (arrival volume × average wait)

SELECT
arrival_hour,
COUNT(*) AS visits,

ROUND(AVG(wait_time_minutes),2) AS avg_wait,

ROUND(
COUNT(*) * AVG(wait_time_minutes),
0
) AS workload_index

FROM ed_visits

GROUP BY arrival_hour

ORDER BY workload_index DESC;


-- Query 8
-- Admission rate by arrival hour

SELECT
arrival_hour,

COUNT(*) AS visits,

SUM(admitted_to_hospital='Yes') AS admitted,

ROUND(
SUM(admitted_to_hospital='Yes')*100.0/
COUNT(*),
2
) AS admission_rate

FROM ed_visits

GROUP BY arrival_hour

ORDER BY arrival_hour;


/*====================================================================
SECTION 9 — RELATIONSHIPS
======================================================================

Business Questions
------------------
1. Does age affect waiting time?
2. Does triage level affect waiting time?
3. Are ambulance arrivals more likely to be admitted?
4. Which region has the longest average visit length?
5. Does arrival hour affect waiting time?
6. Do admitted patients stay longer?

*/


-- Query 1
-- Age group vs waiting time

SELECT
CASE
    WHEN age_years < 18 THEN 'Children'
    WHEN age_years < 40 THEN 'Young Adults'
    WHEN age_years < 65 THEN 'Adults'
    ELSE 'Older Adults'
END AS age_group,

ROUND(AVG(wait_time_minutes),2) AS avg_wait,
COUNT(*) AS patients

FROM ed_visits

GROUP BY age_group;


-- Query 2
-- Triage level vs waiting time

SELECT
triage_level,

ROUND(AVG(wait_time_minutes),2) AS avg_wait,

COUNT(*) AS patients

FROM ed_visits

GROUP BY triage_level

ORDER BY avg_wait;


-- Query 3
-- Ambulance arrival vs admission

SELECT
arrival_by_ambulance,

COUNT(*) AS patients,

SUM(admitted_to_hospital='Yes') AS admitted,

ROUND(
SUM(admitted_to_hospital='Yes')*100.0/
COUNT(*),
2
) AS admission_rate

FROM ed_visits

GROUP BY arrival_by_ambulance;


-- Query 4
-- Region vs visit length

SELECT
region,

ROUND(AVG(visit_length_minutes),2) AS avg_visit_length,

COUNT(*) AS patients

FROM ed_visits

GROUP BY region

ORDER BY avg_visit_length DESC;


-- Query 5
-- Arrival hour vs waiting time

SELECT
arrival_hour,

ROUND(AVG(wait_time_minutes),2) AS avg_wait,

COUNT(*) AS patients

FROM ed_visits

GROUP BY arrival_hour

ORDER BY arrival_hour;


-- Query 6
-- Admission status vs visit length

SELECT
admitted_to_hospital,

ROUND(AVG(visit_length_minutes),2) AS avg_visit,

ROUND(AVG(wait_time_minutes),2) AS avg_wait,

COUNT(*) AS patients

FROM ed_visits

GROUP BY admitted_to_hospital;


/*====================================================================
SECTION 10 — DESCRIPTIVE STATISTICS, OUTLIERS & MISSING DATA
======================================================================

Business Questions
------------------
1. What are the descriptive statistics for key variables?
2. Are there extreme waiting times?
3. Are there unusually long ED stays?
4. Are there abnormal temperatures?
5. Are there implausible ages?
6. Are there abnormal pulse values?
7. Which variables contain missing values?

*/


-- Query 1
-- Age summary statistics

SELECT

ROUND(AVG(age_years),2) AS avg_age,

MIN(age_years) AS youngest,

MAX(age_years) AS oldest,

STDDEV(age_years) AS age_sd

FROM ed_visits;


-- Query 2
-- Waiting time summary statistics

SELECT

ROUND(AVG(wait_time_minutes),2) AS avg_wait,

MIN(wait_time_minutes) AS shortest_wait,

MAX(wait_time_minutes) AS longest_wait,

STDDEV(wait_time_minutes) AS wait_sd

FROM ed_visits;


-- Query 3
-- Visit length summary statistics

SELECT

ROUND(AVG(visit_length_minutes),2) AS avg_visit,

MIN(visit_length_minutes) AS shortest_visit,

MAX(visit_length_minutes) AS longest_visit,

STDDEV(visit_length_minutes) AS visit_sd

FROM ed_visits;


-- Query 4
-- Temperature summary statistics

SELECT

ROUND(AVG(temperature_f),2) AS avg_temp,

MIN(temperature_f) AS min_temp,

MAX(temperature_f) AS max_temp

FROM ed_visits;


-- Query 5
-- Pulse summary statistics

SELECT

ROUND(AVG(pulse_bpm),2) AS avg_pulse,

MIN(pulse_bpm) AS min_pulse,

MAX(pulse_bpm) AS max_pulse

FROM ed_visits;


-- Query 6
-- Waiting time outliers

SELECT

visit_id,
wait_time_minutes

FROM ed_visits

WHERE wait_time_minutes > 300

ORDER BY wait_time_minutes DESC;


-- Query 7
-- Visit length outliers

SELECT

visit_id,
visit_length_minutes

FROM ed_visits

WHERE visit_length_minutes > 1000

ORDER BY visit_length_minutes DESC;


-- Query 8
-- Temperature outliers

SELECT

visit_id,
temperature_f

FROM ed_visits

WHERE temperature_f > 105
OR temperature_f < 95;


-- Query 9
-- Age outliers

SELECT

visit_id,
age_years

FROM ed_visits

WHERE age_years > 100;


-- Query 10
-- Pulse outliers

SELECT

visit_id,
pulse_bpm

FROM ed_visits

WHERE pulse_bpm > 180
OR pulse_bpm < 30;


-- Query 11
-- Missing values by variable

SELECT

COUNT(*) AS total_rows,

SUM(visit_id IS NULL) AS visit_id_missing,

SUM(wait_time_minutes IS NULL) AS wait_missing,

SUM(visit_length_minutes IS NULL) AS visit_length_missing,

SUM(age_years IS NULL) AS age_missing,

SUM(pain_scale IS NULL) AS pain_missing,

SUM(pulse_bpm IS NULL) AS pulse_missing,

SUM(respiratory_rate IS NULL) AS respiratory_missing,

SUM(systolic_bp IS NULL) AS systolic_bp_missing,

SUM(diastolic_bp IS NULL) AS diastolic_bp_missing,

SUM(oxygen_saturation IS NULL) AS oxygen_missing,

SUM(temperature_f IS NULL) AS temperature_missing,

SUM(triage_level IS NULL) AS triage_missing,

SUM(reason_for_visit_code IS NULL) AS reason_missing,

SUM(primary_diagnosis_code IS NULL) AS diagnosis_missing

FROM ed_visits;


-- Query 12
-- Missing value percentages

SELECT

ROUND(
100 * SUM(pain_scale IS NULL) / COUNT(*),
2
) AS pain_missing_pct,

ROUND(
100 * SUM(oxygen_saturation IS NULL) / COUNT(*),
2
) AS oxygen_missing_pct,

ROUND(
100 * SUM(temperature_f IS NULL) / COUNT(*),
2
) AS temperature_missing_pct,

ROUND(
100 * SUM(primary_diagnosis_code IS NULL) / COUNT(*),
2
) AS diagnosis_missing_pct

FROM ed_visits;

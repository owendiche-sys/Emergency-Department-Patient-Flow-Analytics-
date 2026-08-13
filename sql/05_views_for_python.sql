/*
=========================================================
Project : Emergency Department Patient Flow Analytics
File    : 05_views_for_python.sql
Author  : Nimi
Purpose : Create reusable reporting and modelling views
=========================================================

Wait-rate denominator: visits with a valid wait time.
Two-hour definition: wait_time_minutes >= 120.
Four-hour definition: wait_time_minutes > 240.
*/

USE ed_patient_flow_analytics;

CREATE OR REPLACE VIEW vw_ed_patient_flow_summary AS
SELECT
    COUNT(*) AS total_visits,
    SUM(wait_time_minutes IS NOT NULL) AS valid_wait_records,
    ROUND(AVG(wait_time_minutes), 2) AS average_wait_minutes,
    ROUND(AVG(visit_length_minutes), 2) AS average_visit_length_minutes,
    ROUND(100.0 * SUM(admitted_to_hospital = 'Yes') / COUNT(*), 2) AS admission_rate,
    ROUND(100.0 * SUM(arrival_by_ambulance = 'Yes') / COUNT(*), 2) AS ambulance_arrival_rate,
    ROUND(100.0 * SUM(left_without_being_seen = 'Yes') / COUNT(*), 2) AS left_without_being_seen_rate,
    ROUND(
        100.0 * SUM(left_before_treatment_complete = 'Yes') / COUNT(*),
        2
    ) AS left_before_treatment_complete_rate
FROM ed_visits;


CREATE OR REPLACE VIEW vw_ed_wait_kpis AS
SELECT
    COUNT(*) AS total_visits,
    SUM(wait_time_minutes IS NOT NULL) AS valid_wait_records,
    ROUND(AVG(wait_time_minutes), 2) AS average_wait_minutes,
    MIN(wait_time_minutes) AS shortest_wait_minutes,
    MAX(wait_time_minutes) AS longest_wait_minutes,
    SUM(extended_wait_2hr_flag = 1) AS extended_wait_2hr_count,
    ROUND(
        100.0 * SUM(extended_wait_2hr_flag = 1)
        / NULLIF(SUM(wait_time_minutes IS NOT NULL), 0),
        2
    ) AS extended_wait_2hr_rate,
    SUM(long_wait_4hr_flag = 1) AS long_wait_4hr_count,
    ROUND(
        100.0 * SUM(long_wait_4hr_flag = 1)
        / NULLIF(SUM(wait_time_minutes IS NOT NULL), 0),
        2
    ) AS long_wait_4hr_rate
FROM ed_visits;


CREATE OR REPLACE VIEW vw_ed_triage_flow AS
SELECT
    triage_level,
    COUNT(*) AS patient_count,
    SUM(wait_time_minutes IS NOT NULL) AS valid_wait_records,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ed_visits), 2) AS percentage_of_visits,
    ROUND(AVG(wait_time_minutes), 2) AS average_wait_minutes,
    ROUND(AVG(visit_length_minutes), 2) AS average_visit_length_minutes,
    ROUND(100.0 * SUM(admitted_to_hospital = 'Yes') / COUNT(*), 2) AS admission_rate
FROM ed_visits
GROUP BY triage_level;


CREATE OR REPLACE VIEW vw_ed_outcomes AS
SELECT
    COUNT(*) AS total_visits,
    SUM(admitted_to_hospital = 'Yes') AS admitted_count,
    ROUND(100.0 * SUM(admitted_to_hospital = 'Yes') / COUNT(*), 2) AS admission_rate,
    SUM(observation_then_hospitalized = 'Yes') AS observation_then_hospitalized_count,
    ROUND(
        100.0 * SUM(observation_then_hospitalized = 'Yes') / COUNT(*),
        2
    ) AS observation_then_hospitalized_rate,
    SUM(observation_then_discharged = 'Yes') AS observation_then_discharged_count,
    ROUND(
        100.0 * SUM(observation_then_discharged = 'Yes') / COUNT(*),
        2
    ) AS observation_then_discharged_rate,
    SUM(left_without_being_seen = 'Yes') AS left_without_being_seen_count,
    ROUND(
        100.0 * SUM(left_without_being_seen = 'Yes') / COUNT(*),
        2
    ) AS left_without_being_seen_rate,
    SUM(left_before_treatment_complete = 'Yes') AS left_before_treatment_complete_count,
    ROUND(
        100.0 * SUM(left_before_treatment_complete = 'Yes') / COUNT(*),
        2
    ) AS left_before_treatment_complete_rate,
    SUM(left_against_medical_advice = 'Yes') AS left_against_medical_advice_count,
    SUM(died_in_ed = 'Yes') AS died_in_ed_count
FROM ed_visits;


CREATE OR REPLACE VIEW vw_ambulance_summary AS
SELECT
    arrival_by_ambulance,
    COUNT(*) AS patient_count,
    SUM(wait_time_minutes IS NOT NULL) AS valid_wait_records,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ed_visits), 2) AS percentage_of_visits,
    ROUND(AVG(wait_time_minutes), 2) AS average_wait_minutes,
    ROUND(AVG(visit_length_minutes), 2) AS average_visit_length_minutes,
    SUM(admitted_to_hospital = 'Yes') AS admitted_count,
    ROUND(100.0 * SUM(admitted_to_hospital = 'Yes') / COUNT(*), 2) AS admission_rate
FROM ed_visits
GROUP BY arrival_by_ambulance;


CREATE OR REPLACE VIEW vw_region_summary AS
SELECT
    region,
    COUNT(*) AS patient_count,
    SUM(wait_time_minutes IS NOT NULL) AS valid_wait_records,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM ed_visits), 2) AS percentage_of_visits,
    ROUND(AVG(wait_time_minutes), 2) AS average_wait_minutes,
    ROUND(AVG(visit_length_minutes), 2) AS average_visit_length_minutes,
    ROUND(100.0 * SUM(admitted_to_hospital = 'Yes') / COUNT(*), 2) AS admission_rate
FROM ed_visits
GROUP BY region;


CREATE OR REPLACE VIEW vw_monthly_summary AS
SELECT
    visit_month,
    visit_month_name,
    COUNT(*) AS patient_count,
    SUM(wait_time_minutes IS NOT NULL) AS valid_wait_records,
    ROUND(AVG(wait_time_minutes), 2) AS average_wait_minutes,
    ROUND(AVG(visit_length_minutes), 2) AS average_visit_length_minutes,
    ROUND(100.0 * SUM(admitted_to_hospital = 'Yes') / COUNT(*), 2) AS admission_rate
FROM ed_visits
GROUP BY visit_month, visit_month_name;


CREATE OR REPLACE VIEW vw_day_summary AS
SELECT
    visit_day,
    COUNT(*) AS patient_count,
    SUM(wait_time_minutes IS NOT NULL) AS valid_wait_records,
    ROUND(AVG(wait_time_minutes), 2) AS average_wait_minutes,
    ROUND(AVG(visit_length_minutes), 2) AS average_visit_length_minutes,
    ROUND(100.0 * SUM(admitted_to_hospital = 'Yes') / COUNT(*), 2) AS admission_rate
FROM ed_visits
GROUP BY visit_day;


CREATE OR REPLACE VIEW vw_arrival_hour_summary AS
SELECT
    arrival_hour,
    COUNT(*) AS patient_count,
    SUM(wait_time_minutes IS NOT NULL) AS valid_wait_records,
    ROUND(AVG(wait_time_minutes), 2) AS average_wait_minutes,
    ROUND(AVG(visit_length_minutes), 2) AS average_visit_length_minutes,
    ROUND(100.0 * SUM(admitted_to_hospital = 'Yes') / COUNT(*), 2) AS admission_rate
FROM ed_visits
GROUP BY arrival_hour;


CREATE OR REPLACE VIEW vw_business_question_metrics AS
SELECT
    COUNT(*) AS total_visits,
    SUM(wait_time_minutes IS NOT NULL) AS valid_wait_records,
    ROUND(AVG(wait_time_minutes), 2) AS average_wait_minutes,
    ROUND(AVG(visit_length_minutes), 2) AS average_visit_length_minutes,
    ROUND(100.0 * SUM(admitted_to_hospital = 'Yes') / COUNT(*), 2) AS admission_rate,
    ROUND(100.0 * SUM(arrival_by_ambulance = 'Yes') / COUNT(*), 2) AS ambulance_arrival_rate,
    ROUND(
        100.0 * SUM(extended_wait_2hr_flag = 1)
        / NULLIF(SUM(wait_time_minutes IS NOT NULL), 0),
        2
    ) AS extended_wait_2hr_rate,
    ROUND(
        100.0 * SUM(long_wait_4hr_flag = 1)
        / NULLIF(SUM(wait_time_minutes IS NOT NULL), 0),
        2
    ) AS long_wait_4hr_rate,
    ROUND(100.0 * SUM(left_without_being_seen = 'Yes') / COUNT(*), 2) AS left_without_being_seen_rate,
    ROUND(
        100.0 * SUM(left_before_treatment_complete = 'Yes') / COUNT(*),
        2
    ) AS left_before_treatment_complete_rate
FROM ed_visits;


-- Only arrival-time or near-arrival features and target flags are exposed.
-- Post-arrival outcomes and raw wait time are deliberately excluded.
CREATE OR REPLACE VIEW vw_ml_wait_features AS
SELECT
    visit_id,
    visit_month,
    visit_day,
    arrival_hour,
    age_years,
    sex,
    residence_type,
    arrival_by_ambulance,
    ambulance_transfer,
    triage_level,
    pain_scale,
    pulse_bpm,
    respiratory_rate,
    systolic_bp,
    diastolic_bp,
    oxygen_saturation,
    temperature_f,
    chronic_condition_count,
    region,
    metropolitan_status,
    extended_wait_2hr_flag,
    long_wait_4hr_flag
FROM ed_visits
WHERE extended_wait_2hr_flag IS NOT NULL;

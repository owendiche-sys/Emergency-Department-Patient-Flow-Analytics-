/*
=========================================================
Project : Emergency Department Patient Flow Analytics
File    : 03_create_final_table.sql
Author  : Nimi
Purpose : Create and validate the typed analytical table
=========================================================
*/

USE ed_patient_flow_analytics;

DROP TABLE IF EXISTS ed_visits;

CREATE TABLE ed_visits (
    visit_id                           INT PRIMARY KEY,
    visit_month                        TINYINT,
    visit_month_name                   VARCHAR(20),
    visit_day                          VARCHAR(20),
    arrival_time                       TIME,
    arrival_hour                       TINYINT,
    wait_time_minutes                  DECIMAL(10,2),
    visit_length_minutes               DECIMAL(10,2),
    age_years                          INT,
    pain_scale                         DECIMAL(4,1),
    pulse_bpm                          DECIMAL(6,2),
    respiratory_rate                   DECIMAL(6,2),
    systolic_bp                        DECIMAL(6,2),
    diastolic_bp                       DECIMAL(6,2),
    oxygen_saturation                  DECIMAL(5,2),
    chronic_condition_count            INT,
    diagnosis_count                    INT,
    procedure_count                    INT,
    survey_visit_weight                DECIMAL(10,4),
    temperature_f                      DECIMAL(5,2),
    sex                                VARCHAR(10),
    residence_type                     VARCHAR(30),
    arrival_by_ambulance               VARCHAR(10),
    ambulance_transfer                 VARCHAR(30),
    triage_level                       VARCHAR(50),
    reason_for_visit_code              VARCHAR(20),
    primary_diagnosis_code             VARCHAR(20),
    left_without_being_seen            VARCHAR(10),
    left_before_treatment_complete     VARCHAR(10),
    left_against_medical_advice        VARCHAR(10),
    died_in_ed                         VARCHAR(10),
    admitted_to_hospital               VARCHAR(10),
    observation_then_hospitalized      VARCHAR(10),
    observation_then_discharged        VARCHAR(10),
    admission_destination              VARCHAR(50),
    region                             VARCHAR(20),
    metropolitan_status                VARCHAR(20),
    long_wait_4hr_flag                 TINYINT,
    extended_wait_2hr_flag             TINYINT
);

INSERT INTO ed_visits (
    visit_id,
    visit_month,
    visit_month_name,
    visit_day,
    arrival_time,
    arrival_hour,
    wait_time_minutes,
    visit_length_minutes,
    age_years,
    pain_scale,
    pulse_bpm,
    respiratory_rate,
    systolic_bp,
    diastolic_bp,
    oxygen_saturation,
    chronic_condition_count,
    diagnosis_count,
    procedure_count,
    survey_visit_weight,
    temperature_f,
    sex,
    residence_type,
    arrival_by_ambulance,
    ambulance_transfer,
    triage_level,
    reason_for_visit_code,
    primary_diagnosis_code,
    left_without_being_seen,
    left_before_treatment_complete,
    left_against_medical_advice,
    died_in_ed,
    admitted_to_hospital,
    observation_then_hospitalized,
    observation_then_discharged,
    admission_destination,
    region,
    metropolitan_status,
    long_wait_4hr_flag,
    extended_wait_2hr_flag
)
SELECT
    CAST(NULLIF(visit_id, 'NULL') AS UNSIGNED),
    CAST(NULLIF(visit_month, 'NULL') AS UNSIGNED),
    NULLIF(visit_month_name, 'NULL'),
    NULLIF(visit_day, 'NULL'),
    STR_TO_DATE(NULLIF(arrival_time, 'NULL'), '%H:%i'),
    CAST(NULLIF(arrival_hour, 'NULL') AS UNSIGNED),
    CAST(NULLIF(wait_time_minutes, 'NULL') AS DECIMAL(10,2)),
    CAST(NULLIF(visit_length_minutes, 'NULL') AS DECIMAL(10,2)),
    CAST(NULLIF(age_years, 'NULL') AS UNSIGNED),
    CAST(NULLIF(pain_scale, 'NULL') AS DECIMAL(4,1)),
    CAST(NULLIF(pulse_bpm, 'NULL') AS DECIMAL(6,2)),
    CAST(NULLIF(respiratory_rate, 'NULL') AS DECIMAL(6,2)),
    CAST(NULLIF(systolic_bp, 'NULL') AS DECIMAL(6,2)),
    CAST(NULLIF(diastolic_bp, 'NULL') AS DECIMAL(6,2)),
    CAST(NULLIF(oxygen_saturation, 'NULL') AS DECIMAL(5,2)),
    CAST(NULLIF(chronic_condition_count, 'NULL') AS UNSIGNED),
    CAST(NULLIF(diagnosis_count, 'NULL') AS UNSIGNED),
    CAST(NULLIF(procedure_count, 'NULL') AS UNSIGNED),
    CAST(NULLIF(survey_visit_weight, 'NULL') AS DECIMAL(10,4)),
    CAST(NULLIF(temperature_f, 'NULL') AS DECIMAL(5,2)),
    NULLIF(sex, 'NULL'),
    NULLIF(residence_type, 'NULL'),
    NULLIF(arrival_by_ambulance, 'NULL'),
    NULLIF(ambulance_transfer, 'NULL'),
    NULLIF(triage_level, 'NULL'),
    NULLIF(reason_for_visit_code, 'NULL'),
    NULLIF(primary_diagnosis_code, 'NULL'),
    NULLIF(left_without_being_seen, 'NULL'),
    NULLIF(left_before_treatment_complete, 'NULL'),
    NULLIF(left_against_medical_advice, 'NULL'),
    NULLIF(died_in_ed, 'NULL'),
    NULLIF(admitted_to_hospital, 'NULL'),
    NULLIF(observation_then_hospitalized, 'NULL'),
    NULLIF(observation_then_discharged, 'NULL'),
    NULLIF(admission_destination, 'NULL'),
    NULLIF(region, 'NULL'),
    NULLIF(metropolitan_status, 'NULL'),
    CAST(NULLIF(long_wait_4hr_flag, 'NULL') AS UNSIGNED),
    CAST(NULLIF(extended_wait_2hr_flag, 'NULL') AS UNSIGNED)
FROM staging_ed_visits;


-- =====================================
-- VALIDATION CHECKS
-- =====================================

-- Total rows
SELECT COUNT(*) AS total_rows
FROM ed_visits;

-- Duplicate visit IDs
SELECT
    visit_id,
    COUNT(*) AS occurrences
FROM ed_visits
GROUP BY visit_id
HAVING COUNT(*) > 1;

-- Missing wait times
SELECT COUNT(*) AS missing_wait_times
FROM ed_visits
WHERE wait_time_minutes IS NULL;

-- Wait flag totals. Expected: 238 four-hour and 907 two-hour waits.
SELECT
    SUM(long_wait_4hr_flag) AS long_waits,
    SUM(extended_wait_2hr_flag) AS extended_waits
FROM ed_visits;

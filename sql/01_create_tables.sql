/*
=========================================================
Project : Emergency Department Patient Flow Analytics
File    : 01_create_tables.sql
Author  : Nimi
Purpose : Create the project database and table structure
=========================================================
*/

-- Create the project database if it does not already exist
CREATE DATABASE IF NOT EXISTS ed_patient_flow_analytics;

-- Set the newly created database as the active database
USE ed_patient_flow_analytics;

-- Recreate the staging table so the pipeline can be run safely from scratch.
DROP TABLE IF EXISTS staging_ed_visits;

CREATE TABLE staging_ed_visits (

    visit_id                         VARCHAR(255),
    visit_month                      VARCHAR(255),
    visit_month_name                 VARCHAR(255),
    visit_day                        VARCHAR(255),
    arrival_time                     VARCHAR(255),
    arrival_hour                     VARCHAR(255),
    wait_time_minutes                VARCHAR(255),
    visit_length_minutes             VARCHAR(255),

    age_years                        VARCHAR(255),
    pain_scale                       VARCHAR(255),
    pulse_bpm                        VARCHAR(255),
    respiratory_rate                 VARCHAR(255),
    systolic_bp                      VARCHAR(255),
    diastolic_bp                     VARCHAR(255),
    oxygen_saturation                VARCHAR(255),
    chronic_condition_count          VARCHAR(255),

    diagnosis_count                  VARCHAR(255),
    procedure_count                  VARCHAR(255),
    survey_visit_weight              VARCHAR(255),
    temperature_f                    VARCHAR(255),
    sex                              VARCHAR(255),
    residence_type                   VARCHAR(255),
    arrival_by_ambulance             VARCHAR(255),
    ambulance_transfer               VARCHAR(255),

    triage_level                     VARCHAR(255),
    reason_for_visit_code            VARCHAR(255),
    primary_diagnosis_code           VARCHAR(255),
    left_without_being_seen          VARCHAR(255),
    left_before_treatment_complete   VARCHAR(255),
    left_against_medical_advice      VARCHAR(255),
    died_in_ed                       VARCHAR(255),
    admitted_to_hospital             VARCHAR(255),

    observation_then_hospitalized    VARCHAR(255),
    observation_then_discharged      VARCHAR(255),
    admission_destination            VARCHAR(255),
    region                           VARCHAR(255),
    metropolitan_status              VARCHAR(255),
    long_wait_4hr_flag               VARCHAR(255),
    extended_wait_2hr_flag           VARCHAR(255)

);

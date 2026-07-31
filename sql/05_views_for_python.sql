CREATE OR REPLACE VIEW vw_ed_patient_flow_summary AS
SELECT
    COUNT(*) AS total_visits,

    ROUND(AVG(wait_time_minutes),2) AS avg_wait_minutes,

    ROUND(AVG(visit_length_minutes),2) AS avg_visit_length_minutes,

    ROUND(
        100 * SUM(admitted_to_hospital='Yes') / COUNT(*),
        2
    ) AS admission_rate,

    ROUND(
        100 * SUM(arrival_by_ambulance='Yes') / COUNT(*),
        2
    ) AS ambulance_rate

FROM ed_visits;


CREATE OR REPLACE VIEW vw_ed_patient_flow_summary AS
SELECT
    COUNT(*) AS total_visits,

    ROUND(AVG(wait_time_minutes),2) AS avg_wait_minutes,

    ROUND(AVG(visit_length_minutes),2) AS avg_visit_length_minutes,

    ROUND(
        100 * SUM(admitted_to_hospital='Yes') / COUNT(*),
        2
    ) AS admission_rate,

    ROUND(
        100 * SUM(arrival_by_ambulance='Yes') / COUNT(*),
        2
    ) AS ambulance_rate

FROM ed_visits;


CREATE OR REPLACE VIEW vw_ed_wait_kpis AS
SELECT

COUNT(*) AS total_visits,

ROUND(AVG(wait_time_minutes),2) AS average_wait,

MIN(wait_time_minutes) AS shortest_wait,

MAX(wait_time_minutes) AS longest_wait,

ROUND(
100 * SUM(wait_time_minutes > 120)/COUNT(*),
2
) AS pct_over_2_hours,

ROUND(
100 * SUM(wait_time_minutes > 240)/COUNT(*),
2
) AS pct_over_4_hours

FROM ed_visits;


CREATE OR REPLACE VIEW vw_ed_triage_flow AS
SELECT

    triage_level,

    COUNT(*) AS patient_count,

    ROUND(
        100 * COUNT(*) /
        (SELECT COUNT(*) FROM ed_visits),
        2
    ) AS percentage,

    ROUND(AVG(wait_time_minutes),2) AS avg_wait,

    ROUND(AVG(visit_length_minutes),2) AS avg_visit_length,

    ROUND(
        100 * SUM(admitted_to_hospital='Yes') / COUNT(*),
        2
    ) AS admission_rate

FROM ed_visits

GROUP BY triage_level

ORDER BY patient_count DESC;


CREATE OR REPLACE VIEW vw_ed_outcomes AS
SELECT

    admission_destination,

    COUNT(*) AS patient_count,

    ROUND(
        100 * COUNT(*) /
        (SELECT COUNT(*) FROM ed_visits),
        2
    ) AS percentage,

    ROUND(AVG(wait_time_minutes),2) AS avg_wait,

    ROUND(AVG(visit_length_minutes),2) AS avg_visit_length

FROM ed_visits

GROUP BY admission_destination

ORDER BY patient_count DESC;


CREATE OR REPLACE VIEW vw_ambulance_summary AS
SELECT

    arrival_by_ambulance,

    COUNT(*) AS patient_count,

    ROUND(
        100 * COUNT(*) /
        (SELECT COUNT(*) FROM ed_visits),
        2
    ) AS percentage,

    ROUND(AVG(wait_time_minutes),2) AS avg_wait,

    ROUND(AVG(visit_length_minutes),2) AS avg_visit_length,

    SUM(admitted_to_hospital='Yes') AS admitted_patients,

    ROUND(
        100 * SUM(admitted_to_hospital='Yes') /
        COUNT(*),
        2
    ) AS admission_rate

FROM ed_visits

GROUP BY arrival_by_ambulance;


CREATE OR REPLACE VIEW vw_region_summary AS
SELECT

    region,

    COUNT(*) AS patient_count,

    ROUND(
        100 * COUNT(*) /
        (SELECT COUNT(*) FROM ed_visits),
        2
    ) AS percentage,

    ROUND(AVG(wait_time_minutes),2) AS avg_wait,

    ROUND(AVG(visit_length_minutes),2) AS avg_visit_length,

    ROUND(
        100 * SUM(admitted_to_hospital='Yes') /
        COUNT(*),
        2
    ) AS admission_rate

FROM ed_visits

GROUP BY region

ORDER BY patient_count DESC;


CREATE OR REPLACE VIEW vw_monthly_summary AS
SELECT

    visit_month,

    visit_month_name,

    COUNT(*) AS patient_count,

    ROUND(AVG(wait_time_minutes),2) AS avg_wait,

    ROUND(AVG(visit_length_minutes),2) AS avg_visit_length,

    ROUND(
        100 * SUM(admitted_to_hospital='Yes') /
        COUNT(*),
        2
    ) AS admission_rate

FROM ed_visits

GROUP BY visit_month, visit_month_name

ORDER BY visit_month;


CREATE OR REPLACE VIEW vw_day_summary AS
SELECT

    visit_day,

    COUNT(*) AS patient_count,

    ROUND(AVG(wait_time_minutes),2) AS avg_wait,

    ROUND(AVG(visit_length_minutes),2) AS avg_visit_length,

    ROUND(
        100 * SUM(admitted_to_hospital='Yes') /
        COUNT(*),
        2
    ) AS admission_rate

FROM ed_visits

GROUP BY visit_day

ORDER BY FIELD(
    visit_day,
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
);


CREATE OR REPLACE VIEW vw_arrival_hour_summary AS
SELECT

    arrival_hour,

    COUNT(*) AS patient_count,

    ROUND(AVG(wait_time_minutes),2) AS avg_wait,

    ROUND(AVG(visit_length_minutes),2) AS avg_visit_length,

    ROUND(
        100 * SUM(admitted_to_hospital='Yes') /
        COUNT(*),
        2
    ) AS admission_rate

FROM ed_visits

GROUP BY arrival_hour

ORDER BY arrival_hour;


CREATE OR REPLACE VIEW vw_business_question_metrics AS

SELECT

COUNT(*) AS total_visits,

ROUND(AVG(wait_time_minutes),2) AS average_wait_minutes,

ROUND(AVG(visit_length_minutes),2) AS average_visit_length_minutes,

ROUND(
100 * SUM(admitted_to_hospital='Yes')/COUNT(*),
2
) AS admission_rate,

ROUND(
100 * SUM(arrival_by_ambulance='Yes')/COUNT(*),
2
) AS ambulance_arrival_rate,

ROUND(
100 * SUM(wait_time_minutes > 120)/COUNT(*),
2
) AS extended_wait_rate_2hr,

ROUND(
100 * SUM(wait_time_minutes > 240)/COUNT(*),
2
) AS long_wait_rate_4hr,

ROUND(
100 * SUM(left_without_being_seen='Yes')/COUNT(*),
2
) AS left_without_being_seen_rate,

ROUND(
100 * SUM(left_before_treatment_complete='Yes')/COUNT(*),
2
) AS left_before_treatment_rate,

ROUND(
100 * SUM(died_in_ed='Yes')/COUNT(*),
2
) AS ed_mortality_rate

FROM ed_visits;


CREATE OR REPLACE VIEW vw_ml_wait_features AS

SELECT

visit_id,

age_years,

sex,

region,

residence_type,

arrival_hour,

visit_day,

visit_month,

arrival_by_ambulance,

triage_level,

pulse_bpm,

respiratory_rate,

systolic_bp,

diastolic_bp,

oxygen_saturation,

temperature_f,

pain_scale,

wait_time_minutes

FROM ed_visits

WHERE wait_time_minutes IS NOT NULL;


/*
=========================================================
Project : Emergency Department Patient Flow Analytics
File    : 02_load_data.sql
Author  : Nimi
Purpose : Load the clean CSV into the MySQL staging table
=========================================================

Run the MySQL client from the repository root and enable LOCAL INFILE.
If your client resolves relative paths differently, replace the path below
with the absolute path to data/processed/nhamcs_2022_visits_clean.csv.
*/

USE ed_patient_flow_analytics;

TRUNCATE TABLE staging_ed_visits;

LOAD DATA LOCAL INFILE 'data/processed/nhamcs_2022_visits_clean.csv'
INTO TABLE staging_ed_visits
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS;

SELECT COUNT(*) AS staging_rows
FROM staging_ed_visits;

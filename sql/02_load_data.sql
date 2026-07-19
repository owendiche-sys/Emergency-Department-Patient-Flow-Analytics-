LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/nhamcs_2022_visits_clean.csv'
INTO TABLE staging_ed_visits
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
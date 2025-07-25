#!/bin/bash

set -eux

# Create database
psql -v ON_ERROR_STOP=1 <<-EOSQL
  CREATE DATABASE citibike;
EOSQL

# Create table
psql -v ON_ERROR_STOP=1 citibike <<-EOSQL
  CREATE TABLE IF NOT EXISTS tripdata (
    starttime               TIMESTAMP,
    stoptime                TIMESTAMP,
    start_station_id        VARCHAR(25),
    start_station_name      VARCHAR(50),
    start_station_latitude  FLOAT8,
    start_station_longitude FLOAT8,
    end_station_id          VARCHAR(25),
    end_station_name        VARCHAR(50),
    end_station_latitude    FLOAT8,
    end_station_longitude   FLOAT8
  );
EOSQL

# Load data
data_url="https://s3.amazonaws.com/tripdata/${DATA_YEAR}-citibike-tripdata.zip"

wget "${data_url}" -O /tmp/citibike-tripdata.csv.zip # Download data
unzip /tmp/citibike-tripdata.csv.zip -d /tmp # Unzip
ls -l /tmp
filename=$(echo ${data_url} | sed 's:.*/::' | sed 's/\.zip$//') # Determine filename of unzipped CSV (this is the same as the .zip file)
ls -l /tmp/${filename}/
for file in /tmp/${filename}/*.zip; do
  unzip "${file}" -d "/tmp/${filename}/"
done
ls -l /tmp/${filename}/

# Filter lines otherwise full Docker image is 4.18GB, every 8th line results in 890MB
time awk -F',' 'NR == 1 || NR % 8 == 0 {print $3","$4","$6","$5","$9","$10","$8","$7","$11","$12}' /tmp/${filename}/*.csv | grep -v "NULL" | grep -v "started_at" > /tmp/citibike-tripdata.csv # Extract specific columns, write result to new file
time psql -v ON_ERROR_STOP=1 citibike <<-EOSQL
  COPY tripdata
  FROM '/tmp/citibike-tripdata.csv' DELIMITER ',' CSV;
EOSQL

psql -v ON_ERROR_STOP=1 <<-EOSQL
  CREATE USER citi WITH PASSWORD 'cycling';
  GRANT ALL PRIVILEGES ON DATABASE citibike TO citi;
  \c citibike;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO citi;
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO citi;
EOSQL

exit 0

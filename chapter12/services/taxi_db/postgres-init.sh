#!/bin/bash

set -eux

psql -v ON_ERROR_STOP=1 <<-EOSQL
  CREATE DATABASE tlctriprecords;
EOSQL


# Create table
psql -v ON_ERROR_STOP=1 tlctriprecords <<-EOSQL
  CREATE TABLE IF NOT EXISTS triprecords (
    pickup_datetime    TIMESTAMP,
    dropoff_datetime   TIMESTAMP,
    pickup_locationid  INTEGER,
    dropoff_locationid INTEGER,
    trip_distance      NUMERIC(12,2)
  );
EOSQL

# Load data into postgres
for i in {01..12}
do
psql -v ON_ERROR_STOP=1 tlctriprecords <<-EOSQL
    COPY triprecords(pickup_datetime,dropoff_datetime,trip_distance,pickup_locationid,dropoff_locationid)
    FROM '/csvdata/yellowtripdata_${DATA_YEAR}-${i}.csv' DELIMITER ',' CSV HEADER;
EOSQL
done

psql -v ON_ERROR_STOP=1 <<-EOSQL
  CREATE USER taxi WITH PASSWORD 'ridetlc';
  GRANT ALL PRIVILEGES ON DATABASE tlctriprecords TO taxi;
  \c tlctriprecords;
  GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO taxi;
  GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO taxi;
EOSQL

exit 0

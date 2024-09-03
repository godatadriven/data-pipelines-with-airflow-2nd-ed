#!/bin/bash

set -eux

# Load data
url_prefix="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_${DATA_YEAR}"

for month in {01..12}
do
    echo "${url_prefix}-${month}.parquet"
    wget "${url_prefix}-${month}.parquet" -O /data/yellowtripdata_${DATA_YEAR}-${month}.parquet
done

# We need to convert the parquet format to csv
# Also importing all records results in a 6.35GB Docker image
# Therefore we select every 10th line to decrease size and end up with a smaller Docker image
python /convert_pq_to_csv.py

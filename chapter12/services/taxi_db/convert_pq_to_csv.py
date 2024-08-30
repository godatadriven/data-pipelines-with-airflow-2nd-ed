import os
import random

import pyarrow.csv as csv
import pyarrow.parquet as pq

columns=["tpep_pickup_datetime","tpep_dropoff_datetime","trip_distance","PULocationID","DOLocationID"]


DATA_YEAR=os.environ.get("DATA_YEAR", 2023)

for i in range(1, 13):

    table = pq.read_table(f"/data/yellowtripdata_{DATA_YEAR}-{i:02d}.parquet", columns=columns)
    ten_pct_row_indices = random.sample(range(0, table.num_rows), int(table.num_rows / 10))
    ten_percent_data = table.take(ten_pct_row_indices)
    csv.write_csv(ten_percent_data, f"/data/yellowtripdata_{DATA_YEAR}-{i:02d}.csv")

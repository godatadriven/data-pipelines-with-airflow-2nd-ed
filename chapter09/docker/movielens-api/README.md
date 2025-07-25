# Movielens API

This directory contains an API for the Movielens dataset, in a Docker container. It's used as an example API for consumption in Airflow DAGs.

## Data
The data used is an open dataset that can be found [here](https://grouplens.org/datasets/movielens/). While working on this setup, it became clear that 
interactive download of this data on image startup did not reliably work for everyone (the connection tended to be terminated). To prevent this becoming an issue, we decided to include
the data in a zip file in this repository. This guarantees that the Movielens API will *always* spin up. An added bonus is that it's quite a lot quicker. This zip file is called
`ml-2023-ratings.zip`. 

It was generated using the following commands. Note: We filter a time range of the data to reduce the amount of data needed.
```bash
curl -O http://files.grouplens.org/datasets/movielens/ml-latest.zip
unzip ml-latest.zip
cd ml-latest
python3 -m venv .venv
source .venv/bin/activate
pip install pandas
```
Then, within an interactive Python shell, run the following to filter the data to 2023 data only.
```python
import pandas as pd
ratings = pd.read_csv("ratings.csv")
ts_parsed = pd.to_datetime(ratings["timestamp"], unit="s")
ratings = ratings.loc[(ts_parsed >= "2023-01-01") & (ts_parsed < "2023-12-31")]
ratings.to_csv("2023-ratings.csv", index=False)
```
And finally, zip the data again:
```bash
zip -r ml-2023-ratings.zip ./2023-ratings.csv
```

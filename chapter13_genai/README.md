

Run Instructions


# Run Instructions

1) Run `airflow-init` to start the Airflow server
    
    `docker comopose up airflow-init`

2) Run the Docker compose file
    
    `docker-compose up`

3) Once MinIO is running, you can access the MinIO web interface at `http://localhost:9000` with the following credentials:
    
    - Access Key: `airflow`
    - Pass: `apacheairflow`

4) Create an access key in MinIO UI and update the .env file in this repo on the following variables:
    
    * MINIO_ID
    * MINIO_KEY
    * MINIO_KEY_ENCODED


5) Stop docker-compose (ctrl+c) and run it again to apply the changes
    `docker-compose up --build`

6) Run the DAG in Airflow
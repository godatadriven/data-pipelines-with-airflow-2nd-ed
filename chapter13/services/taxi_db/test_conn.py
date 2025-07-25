
from airflow.models.connection import Connection

#    AIRFLOW_CONN_S3: s3://@?host=http://minio:9000&aws_access_key_id=AKIAIOSFODNN7EXAMPLE&aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

conn = Connection(
    conn_id="sample_aws_connection",
    conn_type="aws",
    host="http://minio:9000",
    login="AKIAIOSFODNN7EXAMPLE",  # Reference to AWS Access Key ID
    password="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",  # Reference to AWS Secret Access Key
    extra={
        # Specify extra parameters here
        "endpoint_url": "http://minio:9000",
    },
)

# Generate Environment Variable Name and Connection URI
env_key = f"AIRFLOW_CONN_{conn.conn_id.upper()}"
conn_uri = conn.get_uri()
print(f"{env_key}={conn_uri}")
# AIRFLOW_CONN_SAMPLE_AWS_CONNECTION=aws://AKIAIOSFODNN7EXAMPLE:wJalrXUtnFEMI%2FK7MDENG%2FbPxRfiCYEXAMPLEKEY@/?region_name=eu-central-1



connnohttp = Connection(
    conn_id="sample_aws_connection_nohttp",
    conn_type="aws",
    login="AKIAIOSFODNN7EXAMPLE",  # Reference to AWS Access Key ID
    password="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",  # Reference to AWS Secret Access Key
    extra={
        # Specify extra parameters here
        "endpoint_url": "http://minio:9000",
    },
)

env_key2 = f"AIRFLOW_CONN_{connnohttp.conn_id.upper()}"
conn_uri2 = connnohttp.get_uri()
print(f"{env_key2}={conn_uri2}")

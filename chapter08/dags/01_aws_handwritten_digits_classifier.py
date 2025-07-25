import gzip
import io
import json
import os
import pickle

import pendulum
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.amazon.aws.operators.s3 import S3CopyObjectOperator, S3CreateBucketOperator
from airflow.providers.amazon.aws.operators.sagemaker import (
    SageMakerEndpointOperator,
    SageMakerTrainingOperator,
)
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from sagemaker import image_uris
from sagemaker.amazon.common import write_numpy_to_dense_tensor

BUCKET_NAME=os.environ.get("MNIST_BUCKET")
REGION_NAME=os.environ.get("AWS_REGION")
SAGEMAKER_ROLE=os.environ.get("SAGEMAKER_EXEC_ROLE_ARN")


def _add_bucket_policy():
    # Create a bucket policy
    bucket_policy = {
        "Version": "2012-10-17",
        "Id": "ExamplePolicy01",
        "Statement": [
            {
                "Sid": "ExampleStatement01",
                "Effect": "Allow",
                "Principal": {
                    "AWS": SAGEMAKER_ROLE
                },
                "Action": "s3:*",
                "Resource": [
                    f"arn:aws:s3:::{BUCKET_NAME}/*",
                    f"arn:aws:s3:::{BUCKET_NAME}"
                ]
            }
        ]
    }

    # Convert the policy from JSON dict to string
    bucket_policy = json.dumps(bucket_policy)

    # Set the new policy
    s3hook = S3Hook()
    session = s3hook.get_session(region_name=REGION_NAME)
    s3_client = session.client("s3")
    s3_client.put_bucket_policy(Bucket=BUCKET_NAME, Policy=bucket_policy)

def _extract_mnist_data():                          #B
    s3hook = S3Hook()                               #C
    # Download S3 dataset into memory
    mnist_buffer = io.BytesIO()
    mnist_obj = s3hook.get_key(                     #D
        bucket_name=BUCKET_NAME,
        key="mnist.pkl.gz",
    )

    mnist_obj.download_fileobj(mnist_buffer)
    # Unpack gzip file, extract dataset, convert, upload back to S3
    mnist_buffer.seek(0)

    with gzip.GzipFile(fileobj=mnist_buffer, mode="rb") as f:
        train_set, _, _ = pickle.loads(f.read(), encoding="latin1")
        output_buffer = io.BytesIO()

        write_numpy_to_dense_tensor(
            file=output_buffer,
            array=train_set[0],
            labels=train_set[1],
        )

        output_buffer.seek(0)
        s3hook.load_file_obj(                      #E
            output_buffer,
            key="mnist_data",
            bucket_name=BUCKET_NAME,
            replace=True,
        )

with DAG(
    dag_id="01_aws_handwritten_digits_classifier",
    schedule=None,
    start_date=pendulum.today("UTC").add(days=-3),
):
    create_bucket = S3CreateBucketOperator(
        task_id="create_mnist_bucket",
        bucket_name=BUCKET_NAME,
        region_name=REGION_NAME
    )

    add_bucket_policy = PythonOperator(
        task_id="add_sagemaker_bucket_policy",
        python_callable=_add_bucket_policy,
    )

    download_mnist_data = S3CopyObjectOperator(    #A
        task_id="download_mnist_data",
        source_bucket_name="sagemaker-sample-data-eu-west-1",
        source_bucket_key="algorithms/kmeans/mnist/mnist.pkl.gz",
        dest_bucket_name=BUCKET_NAME,
        dest_bucket_key="mnist.pkl.gz",
    )

    extract_mnist_data = PythonOperator(            #F
        task_id="extract_mnist_data",
        python_callable=_extract_mnist_data,
    )

    sagemaker_train_model = SageMakerTrainingOperator(            #G
        task_id="sagemaker_train_model",
        config={                                                  #H
            "TrainingJobName": "mnistclassifier-{{ logical_date | ts_nodash }}",
            "AlgorithmSpecification": {
                "TrainingImage": image_uris.retrieve(framework="kmeans",region=REGION_NAME),
                "TrainingInputMode": "File",
            },
            "HyperParameters": {"k": "10", "feature_dim": "784"},
            "InputDataConfig": [
                {
                    "ChannelName": "train",
                    "DataSource": {
                        "S3DataSource": {
                            "S3DataType": "S3Prefix",
                            "S3Uri": f"s3://{BUCKET_NAME}/mnist_data",
                            "S3DataDistributionType": "FullyReplicated",
                        }
                    },
                }
            ],
            "OutputDataConfig": {"S3OutputPath": f"s3://{BUCKET_NAME}/mnistclassifier-output"},
            "ResourceConfig": {
                "InstanceType": "ml.c4.xlarge",
                "InstanceCount": 1,
                "VolumeSizeInGB": 10,
            },
            "RoleArn": SAGEMAKER_ROLE,
            "StoppingCondition": {"MaxRuntimeInSeconds": 24 * 60 * 60},
        },
        wait_for_completion=True,                              #I
        print_log=True,                                        #I
        check_interval=10,
    )

    sagemaker_deploy_model = SageMakerEndpointOperator(       #J
        task_id="sagemaker_deploy_model",
        wait_for_completion=True,
        config={
            "Model": {
                "ModelName": "mnistclassifier-{{ logical_date | ts_nodash }}",
                "PrimaryContainer": {
                    "Image": image_uris.retrieve(framework="kmeans",region=REGION_NAME),
                    "ModelDataUrl": (
                        f"s3://{BUCKET_NAME}/mnistclassifier-output/"
                        "mnistclassifier-{{ logical_date | ts_nodash }}/"
                        "output/model.tar.gz"
                    ), # this will link the model and the training job
                },
                "ExecutionRoleArn": SAGEMAKER_ROLE,
            },
            "EndpointConfig": {
                "EndpointConfigName": "mnistclassifier-{{ logical_date | ts_nodash }}",
                "ProductionVariants": [
                {
                    "InitialInstanceCount": 1,
                    "InstanceType": "ml.t2.medium",
                    "ModelName": "mnistclassifier-{{ logical_date | ts_nodash }}",
                    "VariantName": "AllTraffic",
                }],
            },
            "Endpoint": {
                "EndpointConfigName": "mnistclassifier-{{ logical_date | ts_nodash }}",
                "EndpointName": "mnistclassifier",
            },
        },
    )

    create_bucket >> add_bucket_policy >> download_mnist_data >> extract_mnist_data >> sagemaker_train_model >> sagemaker_deploy_model

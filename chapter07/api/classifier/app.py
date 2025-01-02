import json
import os
from io import BytesIO

import boto3
from botocore.config import Config
import numpy as np
from PIL import Image
from chalice import Chalice, Response
from sagemaker.amazon.common import RecordSerializer

app = Chalice(app_name="number-classifier")
REGION_NAME=os.environ.get('AWS_REGION')


@app.route("/", methods=["POST"], content_types=["image/jpeg"])
def predict():
    """
    Provide this endpoint an image in jpeg format.
    The image should be equal in size to the training images (28x28).
    """
    img = Image.open(BytesIO(app.current_request.raw_body)).convert("L")  #A
    img_arr = np.array(img, dtype=np.float32)                             #A
    runtime = boto3.Session().client(
        service_name="sagemaker-runtime",
        region_name=REGION_NAME,
        config=Config(signature_version='s3v4')
    )
    response = runtime.invoke_endpoint(                           #B
        EndpointName="mnistclassifier",
        ContentType="application/x-recordio-protobuf",
        Body=RecordSerializer("application/x-recordio-protobuf").serialize(img_arr.flatten()),
    )
    result = json.loads(response["Body"].read().decode("utf-8"))         #C
    return Response(
        result,
        status_code=200,
        headers={"Content-Type": "application/json"},
    )

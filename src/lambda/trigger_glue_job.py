import json
import os
import boto3
import urllib.parse
from datetime import datetime

# Initialize Glue client
glue_client = boto3.client("glue")


def lambda_handler(event, context):
    """
    Lambda function handler to trigger a Glue ETL job when new data is uploaded to S3.

    Parameters:
    - event: The event dict containing S3 bucket and object details
    - context: Lambda context object

    Returns:
    - Response with details about the triggered Glue job
    """
    print("Received event:", json.dumps(event))

    # Get environment variables
    glue_job_name = os.environ.get("GLUE_JOB_NAME")
    processed_bucket = os.environ.get("PROCESSED_BUCKET")

    # Get bucket and object info from the event
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(event["Records"][0]["s3"]["object"]["key"])

    print(f"File uploaded: s3://{bucket}/{key}")

    # Extract file name for job parameters
    # Might contain invalid characters for Glue job arguments
    file_name = os.path.basename(key)

    # Get timestamp for job run
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # Start Glue job with parameters
    try:
        response = glue_client.start_job_run(
            JobName=glue_job_name,
            Arguments={
                "--input_file_path": f"s3://{bucket}/{key}",
                "--destination_bucket": processed_bucket,
                "--job_run_id": f"job-run-{timestamp}",
            },
        )

        job_run_id = response["JobRunId"]
        print(f"Started Glue job {glue_job_name} with run ID: {job_run_id}")

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Glue job triggered successfully",
                    "jobName": glue_job_name,
                    "jobRunId": job_run_id,
                    "processedFile": key,
                }
            ),
        }

    except Exception as e:
        print(f"Error starting Glue job: {str(e)}")
        raise e

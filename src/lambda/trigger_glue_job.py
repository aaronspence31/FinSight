import json
import boto3
import os
from urllib.parse import unquote_plus


def lambda_handler(event, context):
    """
    Lambda function that triggers a Glue ETL job when a new file is uploaded to S3.
    Passes input and output bucket information to the Glue job.
    """
    try:
        # Get the S3 event details
        print("Processing S3 event:", json.dumps(event))

        # Get the bucket and key for the uploaded file
        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = unquote_plus(event["Records"][0]["s3"]["object"]["key"])

        print(f"File uploaded: s3://{bucket}/{key}")

        # Skip processing if this is not a CSV file
        if not key.lower().endswith(".csv"):
            print(f"Skipping non-CSV file: {key}")
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {"message": "File skipped (not a CSV)", "file": key}
                ),
            }

        # Get Glue job name from environment variable
        glue_job_name = os.environ.get("GLUE_JOB_NAME")
        if not glue_job_name:
            raise ValueError("GLUE_JOB_NAME environment variable not set")

        # Get output bucket from environment variable or construct it
        # You can set this as an environment variable or derive it from the input bucket
        raw_bucket = f"s3://{bucket}/"
        processed_bucket = os.environ.get("PROCESSED_BUCKET")

        if not processed_bucket:
            # If not provided as env var, derive it based on naming convention
            if "raw-input" in bucket:
                processed_bucket = (
                    f"s3://{bucket.replace('raw-input', 'processed-output')}/"
                )
            else:
                processed_bucket = f"s3://finsight-dev-processed-output-31v4pvuy/"
        else:
            # Ensure the processed bucket has the s3:// prefix when it comes from env var
            if not processed_bucket.startswith("s3://"):
                processed_bucket = f"s3://{processed_bucket}/"
            elif not processed_bucket.endswith("/"):
                processed_bucket = f"{processed_bucket}/"

        print(f"Input bucket: {raw_bucket}")
        print(f"Output bucket: {processed_bucket}")

        # Initialize Glue client
        glue_client = boto3.client("glue")

        # Start Glue job with arguments
        response = glue_client.start_job_run(
            JobName=glue_job_name,
            Arguments={
                "--input_bucket": raw_bucket,
                "--output_bucket": processed_bucket,
                "--file_name": key,
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
                    "inputBucket": raw_bucket,
                    "outputBucket": processed_bucket,
                }
            ),
        }

    except Exception as e:
        print(f"Error starting Glue job: {str(e)}")
        raise e

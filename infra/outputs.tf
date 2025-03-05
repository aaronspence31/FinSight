################################################
############## S3 Bucket Outputs ###############
################################################
# These outputs provide access to bucket names and website endpoints

output "raw_data_bucket" {
  description = "Name of the S3 bucket for raw data"
  value       = aws_s3_bucket.raw_data.bucket
  # Used for uploading CSV files to trigger the ETL pipeline
}

output "processed_data_bucket" {
  description = "Name of the S3 bucket for processed data"
  value       = aws_s3_bucket.processed_data.bucket
  # Stores both processed data and Glue scripts
}

output "website_bucket" {
  description = "Name of the S3 bucket for the website"
  value       = aws_s3_bucket.website.bucket
  # Bucket that hosts the static website files
}

output "website_endpoint" {
  description = "Website endpoint"
  value       = aws_s3_bucket_website_configuration.website.website_endpoint
  # The S3 endpoint URL for the static website
}

output "website_url" {
  description = "Website URL"
  value       = "http://${aws_s3_bucket_website_configuration.website.website_endpoint}"
  # The complete URL to access the website in a browser
}

################################################
############## Lambda Outputs ##################
################################################
# These outputs provide information about the Lambda function that triggers the ETL process

output "lambda_function_arn" {
  description = "The ARN of the Lambda function"
  value       = aws_lambda_function.trigger_glue_job.arn
  # Useful for creating additional triggers or permissions
}

output "lambda_function_name" {
  description = "The name of the Lambda function"
  value       = aws_lambda_function.trigger_glue_job.function_name
  # Used when updating the function or viewing CloudWatch logs
}

output "lambda_role_arn" {
  description = "The ARN of the IAM role used by the Lambda function"
  value       = aws_iam_role.lambda_role.arn
  # IAM role that determines Lambda's permissions
}

output "s3_notification_configuration" {
  description = "The S3 bucket notification configuration"
  value       = aws_s3_bucket_notification.bucket_notification.id
  # Configuration that triggers Lambda when files are uploaded to S3
}

################################################
############## Glue Job Outputs ################
################################################
# These outputs provide details about the Glue ETL job configuration

output "glue_job_name" {
  description = "Name of the Glue ETL job"
  value       = aws_glue_job.etl_job.name
  # Used when starting or monitoring the ETL job
}

output "glue_job_role_arn" {
  description = "ARN of the IAM role used by the Glue job"
  value       = aws_iam_role.glue_role.arn
  # IAM role that determines Glue's permissions to access resources
}

output "glue_job_script_location" {
  description = "S3 location of the Glue job script"
  value       = aws_glue_job.etl_job.command[0].script_location
  # Path to the Python script that Glue executes for ETL
}

output "glue_worker_type" {
  description = "Worker type used by the Glue job"
  value       = aws_glue_job.etl_job.worker_type
  # G.2X workers provide 2 DPUs per worker (8 vCPU, 32GB memory)
}

output "glue_number_of_workers" {
  description = "Number of workers used by the Glue job"
  value       = aws_glue_job.etl_job.number_of_workers
  # 3 workers process the data in parallel for better performance
}

################################################
############## Athena Outputs ##################
################################################
# These outputs provide details about Athena configuration for querying processed data

output "athena_database_name" {
  description = "Name of the Athena database"
  value       = aws_athena_database.finsight_db.name
  # Database name used in SQL queries: SELECT * FROM {database}.table
}

output "athena_workgroup_name" {
  description = "Name of the Athena workgroup"
  value       = aws_athena_workgroup.finsight_workgroup.name
  # Workgroup that manages Athena query execution settings
}

output "athena_results_location" {
  description = "S3 location for Athena query results"
  value       = aws_athena_workgroup.finsight_workgroup.configuration[0].result_configuration[0].output_location
  # S3 path where Athena stores query results
}

################################################
############## IAM Policy Outputs ##############
################################################
# These outputs provide information about IAM policies for service access

output "glue_iam_policy_arn" {
  description = "ARN of the IAM policy for Glue S3 access"
  value       = aws_iam_policy.glue_s3_access.arn
  # Policy that grants Glue permissions to read/write to S3 buckets
}

################################################
############## Summary Outputs #################
################################################
# These outputs provide comprehensive views of the entire infrastructure

output "data_pipeline_summary" {
  description = "Summary of the data pipeline components"
  value = {
    raw_data_bucket     = aws_s3_bucket.raw_data.bucket
    processed_bucket    = aws_s3_bucket.processed_data.bucket
    website_url         = "http://${aws_s3_bucket_website_configuration.website.website_endpoint}"
    lambda_trigger_name = aws_lambda_function.trigger_glue_job.function_name
    glue_job_name       = aws_glue_job.etl_job.name
    athena_database     = aws_athena_database.finsight_db.name
    environment         = var.environment
    project             = var.project_name
  }
  # Consolidated overview of all key pipeline components
  # Useful for documentation and quick reference
}

output "connection_instructions" {
  description = "Instructions for connecting to different components"
  value = {
    website      = "Visit http://${aws_s3_bucket_website_configuration.website.website_endpoint} in your browser"
    athena_query = "Use the AWS console or CLI to query data with: SELECT * FROM ${aws_athena_database.finsight_db.name}.stock_data LIMIT 10"
    upload_data  = "Upload CSV data to s3://${aws_s3_bucket.raw_data.bucket}/ to trigger the ETL pipeline"
  }
  # User-friendly instructions for interacting with the infrastructure
  # Can be used in documentation or shared with team members
}

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
############## API Gateway Outputs #############
################################################
# These outputs provide access information for the API Gateway

output "api_gateway_url" {
  description = "URL for the API Gateway endpoint"
  value       = "${aws_api_gateway_deployment.finsight_api_deployment.invoke_url}${aws_api_gateway_resource.query.path}"
  # The full URL to call for executing Athena queries
}

output "api_gateway_id" {
  description = "ID of the API Gateway REST API"
  value       = aws_api_gateway_rest_api.finsight_api.id
  # Used for management and reference in AWS console
}

output "api_stage_name" {
  description = "Deployment stage name for the API"
  value       = var.environment
  # The environment stage name used in the API URL
}

################################################
########## Athena Query Lambda Outputs #########
################################################
# These outputs provide information about the Lambda that executes Athena queries

output "athena_lambda_function_arn" {
  description = "The ARN of the Athena query Lambda function"
  value       = aws_lambda_function.athena_query.arn
  # Reference ARN for the Lambda function that executes Athena queries
}

output "athena_lambda_function_name" {
  description = "The name of the Athena query Lambda function"
  value       = aws_lambda_function.athena_query.function_name
  # Used when updating the function or viewing CloudWatch logs
}

output "athena_lambda_role_arn" {
  description = "The ARN of the IAM role used by the Athena query Lambda"
  value       = aws_iam_role.athena_lambda_role.arn
  # IAM role that determines Lambda's permissions for Athena access
}

################################################
########## Website Integration Outputs #########
################################################
# These outputs provide information for website-backend integration

output "website_api_config" {
  description = "Configuration details for website to connect to API"
  value = {
    api_url      = "${aws_api_gateway_deployment.finsight_api_deployment.invoke_url}${aws_api_gateway_resource.query.path}"
    method       = "POST"
    content_type = "application/json"
    database     = aws_athena_database.finsight_db.name
    table_name   = "stock_data" # This matches your ETL job's table name
  }
  # Complete configuration for the website JavaScript to connect to the API
}

# Update the connection_instructions with API information
output "updated_connection_instructions" {
  description = "Updated instructions for connecting to different components"
  value = {
    website      = "Visit http://${aws_s3_bucket_website_configuration.website.website_endpoint} in your browser"
    athena_query = "Use the AWS console or CLI to query data with: SELECT * FROM ${aws_athena_database.finsight_db.name}.stock_data LIMIT 10"
    upload_data  = "Upload CSV data to s3://${aws_s3_bucket.raw_data.bucket}/ to trigger the ETL pipeline"
    api_usage    = "Make POST requests to ${aws_api_gateway_deployment.finsight_api_deployment.invoke_url}${aws_api_gateway_resource.query.path} with your query details"
  }
  # Enhanced instructions including API connection details
}

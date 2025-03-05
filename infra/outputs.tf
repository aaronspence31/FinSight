output "raw_data_bucket" {
  description = "Name of the S3 bucket for raw data"
  value       = aws_s3_bucket.raw_data.bucket
}

output "processed_data_bucket" {
  description = "Name of the S3 bucket for processed data"
  value       = aws_s3_bucket.processed_data.bucket
}

output "website_bucket" {
  description = "Name of the S3 bucket for the website"
  value       = aws_s3_bucket.website.bucket
}

output "website_endpoint" {
  description = "Website endpoint"
  value       = aws_s3_bucket_website_configuration.website.website_endpoint
}

output "website_url" {
  description = "Website URL"
  value       = "http://${aws_s3_bucket_website_configuration.website.website_endpoint}"
}
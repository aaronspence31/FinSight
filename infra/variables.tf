variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "finsight"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "raw_bucket_suffix" {
  description = "Suffix for the raw data S3 bucket name"
  type        = string
  default     = "raw-input"
}

variable "processed_bucket_suffix" {
  description = "Suffix for the processed data S3 bucket name"
  type        = string
  default     = "processed-output"
}

variable "website_bucket_suffix" {
  description = "Suffix for the website S3 bucket name"
  type        = string
  default     = "website"
}
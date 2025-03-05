# Generate a random suffix to ensure bucket names are globally unique
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 bucket for raw financial data input
resource "aws_s3_bucket" "raw_data" {
  bucket = "${var.project_name}-${var.environment}-${var.raw_bucket_suffix}-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "Raw Financial Data"
    Environment = var.environment
    Project     = var.project_name
  }
}

# S3 bucket for processed financial data output
resource "aws_s3_bucket" "processed_data" {
  bucket = "${var.project_name}-${var.environment}-${var.processed_bucket_suffix}-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "Processed Financial Data"
    Environment = var.environment
    Project     = var.project_name
  }
}

# S3 bucket for dashboard website
resource "aws_s3_bucket" "website" {
  bucket = "${var.project_name}-${var.environment}-${var.website_bucket_suffix}-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "FinSight Dashboard"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Configure the website bucket for static website hosting
resource "aws_s3_bucket_website_configuration" "website" {
  bucket = aws_s3_bucket.website.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}

# Make the website bucket publicly accessible
resource "aws_s3_bucket_public_access_block" "website" {
  bucket = aws_s3_bucket.website.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# Apply public read access to the website bucket
resource "aws_s3_bucket_policy" "website" {
  bucket = aws_s3_bucket.website.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.website.arn}/*"
      },
    ]
  })

  # Wait for the public access block to be configured before applying the policy
  depends_on = [aws_s3_bucket_public_access_block.website]
}

# IAM role for Lambda to access AWS services
resource "aws_iam_role" "lambda_role" {
  name = "finsight-lambda-trigger-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "Lambda Execution Role"
    Environment = var.environment
    Project     = var.project_name
  }
}

# IAM policy for Lambda to access S3 and start Glue job
resource "aws_iam_policy" "lambda_policy" {
  name        = "finsight-lambda-trigger-policy"
  description = "Policy for Lambda to access S3 and start Glue job"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.raw_data.arn,
          "${aws_s3_bucket.raw_data.arn}/*"
        ]
      },
      {
        Action = [
          "glue:StartJobRun",
          "glue:GetJobRun",
          "glue:GetJobRuns",
          "glue:BatchStopJobRun"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Attach IAM policy to IAM role
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Lambda function to trigger Glue job
resource "aws_lambda_function" "trigger_glue_job" {
  function_name = "finsight-trigger-etl-job"
  description   = "Triggers Glue ETL job when new data is uploaded to S3"
  filename      = "${path.module}/../src/lambda/trigger_glue_job.zip"
  handler       = "trigger_glue_job.lambda_handler"
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_role.arn
  environment {
    variables = {
      GLUE_JOB_NAME = "finsight-etl-job"
      PROCESSED_BUCKET = aws_s3_bucket.processed_data.bucket
    }
  }
  timeout       = 60
  memory_size   = 128
  tags = {
    Name        = "ETL Trigger Function"
    Environment = var.environment
    Project     = var.project_name
  }
}

# S3 notification to trigger Lambda when object is created
resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = aws_s3_bucket.raw_data.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.trigger_glue_job.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = ""
    filter_suffix       = ".csv"
  }

  # Ensure Lambda permissions are in place before notification
  depends_on = [aws_lambda_permission.allow_bucket]
}

# Permission for S3 to invoke Lambda
resource "aws_lambda_permission" "allow_bucket" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trigger_glue_job.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.raw_data.arn
}
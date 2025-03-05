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
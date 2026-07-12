provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "neuraldocs_bucket" {
  bucket = "neuraldocs-rag-documents-bucket"
}

resource "aws_lambda_function" "neuraldocs_api" {
  function_name = "neuraldocs-api"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  image_uri     = "YOUR_ECR_REPOSITORY_URI:latest"
}

resource "aws_iam_role" "lambda_role" {
  name = "neuraldocs-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}


variable "environment" {
  description = "Deployment environment (dev or prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment must be either 'dev' or 'prod'."
  }
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket to store stock data"
  type        = string
  default     = "stock-data-bucket"
}

variable "scraper_api_key" {
  description = "API key for ScraperAPI service"
  type        = string
  sensitive   = true
}

variable "lambda_memory_size" {
  description = "Memory size for Lambda function in MB"
  type        = number
  default     = 256
}

variable "lambda_timeout" {
  description = "Timeout for Lambda function in seconds"
  type        = number
  default     = 60
}

variable "api_throttle_rate_limit" {
  description = "API Gateway throttle rate limit"
  type        = number
  default     = 5
}

variable "api_throttle_burst_limit" {
  description = "API Gateway throttle burst limit"
  type        = number
  default     = 10
}

variable "api_quota_limit" {
  description = "API Gateway quota limit"
  type        = number
  default     = 100
}

variable "api_quota_period" {
  description = "API Gateway quota period"
  type        = string
  default     = "DAY"
  
  validation {
    condition     = contains(["DAY", "WEEK", "MONTH"], var.api_quota_period)
    error_message = "API quota period must be one of: DAY, WEEK, MONTH."
  }
}

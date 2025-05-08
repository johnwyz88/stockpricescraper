# Stock Price Scraper - AWS Deployment Guide

This guide provides instructions for deploying the Stock Price Scraper Lambda function to AWS using the AWS SAM CLI and CloudFormation.

## Prerequisites

Before deploying, ensure you have the following:

1. **AWS CLI** installed and configured with appropriate credentials
   ```bash
   aws configure
   ```

2. **AWS SAM CLI** installed
   ```bash
   pip install aws-sam-cli
   ```

3. **ScraperAPI Key** for web scraping functionality

## Deployment Options

### Option 1: Using the Deployment Script

The simplest way to deploy is using the provided deployment script:

1. Make the script executable:
   ```bash
   chmod +x deploy.sh
   ```

2. Run the deployment script with required parameters:
   ```bash
   ./deploy.sh --api-key YOUR_SCRAPER_API_KEY --environment dev --region us-east-1
   ```

   Additional optional parameters:
   - `--stack-name`: CloudFormation stack name (default: stock-price-scraper)
   - `--s3-bucket`: S3 bucket name for storing stock data (default: auto-generated)

### Option 2: Manual Deployment with AWS SAM

1. Navigate to the infrastructure directory:
   ```bash
   cd infrastructure
   ```

2. Build the Lambda package:
   ```bash
   cd ../scraper
   pip install -r requirements.txt -t ./package
   cp *.py ./package/
   cd ./package
   zip -r ../deployment-package.zip .
   cd ..
   ```

3. Deploy using SAM CLI:
   ```bash
   cd ../infrastructure
   sam deploy \
     --template-file template.yaml \
     --stack-name stock-price-scraper \
     --parameter-overrides \
       Environment=dev \
       ScraperApiKey=YOUR_SCRAPER_API_KEY \
       S3BucketName=your-stock-data-bucket \
     --capabilities CAPABILITY_IAM \
     --region us-east-1
   ```

### Option 3: Using Terraform for API Gateway

If you prefer using Terraform for the API Gateway configuration:

1. Initialize Terraform:
   ```bash
   cd infrastructure
   terraform init
   ```

2. Create a `terraform.tfvars` file with your configuration:
   ```
   environment = "dev"
   aws_region = "us-east-1"
   s3_bucket_name = "your-stock-data-bucket"
   scraper_api_key = "YOUR_SCRAPER_API_KEY"
   ```

3. Apply the Terraform configuration:
   ```bash
   terraform apply
   ```

## Verifying Deployment

After deployment, verify that everything is working correctly:

1. Check the CloudFormation stack status:
   ```bash
   aws cloudformation describe-stacks --stack-name stock-price-scraper
   ```

2. Verify the Lambda function:
   ```bash
   aws lambda get-function --function-name stock-scraper-dev
   ```

3. Test the Lambda function with a sample event:
   ```bash
   aws lambda invoke \
     --function-name stock-scraper-dev \
     --payload file://events/test_event.json \
     output.json
   ```

4. Check the API Gateway endpoint:
   ```bash
   # Get the API Gateway URL from CloudFormation outputs
   API_URL=$(aws cloudformation describe-stacks \
     --stack-name stock-price-scraper \
     --query "Stacks[0].Outputs[?OutputKey=='StockScraperApi'].OutputValue" \
     --output text)
   
   # Test the API endpoint
   curl -X POST \
     -H "Content-Type: application/json" \
     -H "x-api-key: YOUR_API_KEY" \
     -d '{"stock_symbols":["nike"],"start_date":"2023-01-01","end_date":"2023-01-31","output_format":"json"}' \
     $API_URL
   ```

## Troubleshooting

If you encounter issues during deployment:

1. Check CloudWatch Logs:
   ```bash
   aws logs get-log-events \
     --log-group-name /aws/lambda/stock-scraper-dev \
     --log-stream-name $(aws logs describe-log-streams \
       --log-group-name /aws/lambda/stock-scraper-dev \
       --order-by LastEventTime \
       --descending \
       --limit 1 \
       --query "logStreams[0].logStreamName" \
       --output text)
   ```

2. Validate the CloudFormation template:
   ```bash
   aws cloudformation validate-template --template-body file://template.yaml
   ```

3. Check for S3 bucket permissions:
   ```bash
   aws s3api get-bucket-policy --bucket your-stock-data-bucket
   ```

## Cleaning Up

To remove all deployed resources:

1. Using CloudFormation:
   ```bash
   aws cloudformation delete-stack --stack-name stock-price-scraper
   ```

2. Using Terraform (if used):
   ```bash
   terraform destroy
   ```

## Security Considerations

- The API Gateway is configured with API key authentication
- The Lambda function has minimal IAM permissions (S3 access only)
- All S3 buckets have public access blocked
- Data is stored with a 30-day lifecycle policy

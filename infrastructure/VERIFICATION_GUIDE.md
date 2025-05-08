# Stock Price Scraper - Lambda Function Verification Guide

This guide provides instructions for verifying the deployment of the Stock Price Scraper Lambda function on AWS.

## Prerequisites

Before verification, ensure you have:

1. **AWS CLI** installed and configured with appropriate credentials
   ```bash
   aws configure
   ```

2. **Deployed Lambda Function** using the instructions in the DEPLOYMENT_GUIDE.md

3. **API Gateway Endpoint URL** from the CloudFormation stack outputs

## Verification Steps

### 1. Verify CloudFormation Stack

First, check that the CloudFormation stack was created successfully:

```bash
aws cloudformation describe-stacks --stack-name stock-price-scraper
```

Look for `"StackStatus": "CREATE_COMPLETE"` in the output.

### 2. Verify Lambda Function

Check that the Lambda function exists and is configured correctly:

```bash
aws lambda get-function --function-name stock-scraper-dev
```

Verify the following in the output:
- Runtime is Python 3.9
- Handler is set to `lambda_handler.lambda_handler`
- Environment variables include `SCRAPER_API_KEY`, `S3_BUCKET_NAME`, and `AWS_REGION`
- Memory size is at least 256MB
- Timeout is set to 60 seconds

### 3. Test Lambda Function Directly

Invoke the Lambda function directly with a test event:

```bash
aws lambda invoke \
  --function-name stock-scraper-dev \
  --payload file://events/test_event.json \
  --cli-binary-format raw-in-base64-out \
  output.json

# View the output
cat output.json
```

Expected successful response:
```json
{
  "statusCode": 200,
  "body": {
    "message": "Stock data scraped successfully",
    "data": {
      "s3_uri": "s3://stock-data-bucket/data/stock_data_nike-coca-cola-co-microsoft-corp_20230501123456.json",
      "download_url": "https://presigned-url.example.com",
      "expiration": "1 hour",
      "stock_symbols": ["nike", "coca-cola-co", "microsoft-corp"],
      "start_date": "2023-01-01",
      "end_date": "2023-01-31",
      "output_format": "json"
    }
  }
}
```

### 4. Verify API Gateway Integration

Test the API Gateway endpoint:

```bash
# Get the API Gateway URL from CloudFormation outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name stock-price-scraper \
  --query "Stacks[0].Outputs[?OutputKey=='StockScraperApi'].OutputValue" \
  --output text)

# Get the API Key
API_KEY=$(aws apigateway get-api-keys \
  --name-query "stock-scraper-api-key-dev" \
  --include-values \
  --query "items[0].value" \
  --output text)

# Test the API endpoint
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"stock_symbols":["nike"],"start_date":"2023-01-01","end_date":"2023-01-31","output_format":"json"}' \
  $API_URL
```

### 5. Verify S3 Bucket and Permissions

Check that the S3 bucket exists and has the correct permissions:

```bash
# Get the S3 bucket name from CloudFormation outputs
S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name stock-price-scraper \
  --query "Stacks[0].Outputs[?OutputKey=='StockDataBucket'].OutputValue" \
  --output text)

# Check bucket exists
aws s3api head-bucket --bucket $S3_BUCKET

# Check bucket policy
aws s3api get-bucket-policy --bucket $S3_BUCKET

# List objects in the bucket (after running a test)
aws s3 ls s3://$S3_BUCKET/data/
```

### 6. Check CloudWatch Logs

Examine the CloudWatch logs to verify the Lambda function is executing correctly:

```bash
# Get the latest log stream
LOG_STREAM=$(aws logs describe-log-streams \
  --log-group-name /aws/lambda/stock-scraper-dev \
  --order-by LastEventTime \
  --descending \
  --limit 1 \
  --query "logStreams[0].logStreamName" \
  --output text)

# View the logs
aws logs get-log-events \
  --log-group-name /aws/lambda/stock-scraper-dev \
  --log-stream-name $LOG_STREAM
```

Look for successful execution logs and any potential errors.

## Testing Different Scenarios

### Test with Different Output Formats

Test the Lambda function with CSV output:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"stock_symbols":["nike"],"start_date":"2023-01-01","end_date":"2023-01-31","output_format":"csv"}' \
  $API_URL
```

### Test with Multiple Stock Symbols

Test the Lambda function with multiple stock symbols:

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"stock_symbols":["nike","coca-cola-co","microsoft-corp"],"start_date":"2023-01-01","end_date":"2023-01-31","output_format":"json"}' \
  $API_URL
```

### Test Error Handling

Test the Lambda function with invalid input:

```bash
# Test with empty stock symbols
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"stock_symbols":[],"start_date":"2023-01-01","end_date":"2023-01-31","output_format":"json"}' \
  $API_URL

# Test with invalid date format
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"stock_symbols":["nike"],"start_date":"invalid-date","end_date":"2023-01-31","output_format":"json"}' \
  $API_URL
```

## Troubleshooting

If verification fails, check the following:

1. **Lambda Function Configuration**:
   - Ensure the Lambda function has the correct IAM permissions
   - Verify environment variables are set correctly
   - Check that the function timeout is sufficient (60 seconds or more)

2. **API Gateway Configuration**:
   - Verify the API Gateway is correctly integrated with the Lambda function
   - Check that the API Gateway has the correct resource path and method
   - Ensure CORS is properly configured if accessing from a browser

3. **S3 Bucket Permissions**:
   - Verify the Lambda function has permission to write to the S3 bucket
   - Check that the S3 bucket exists and is accessible

4. **CloudWatch Logs**:
   - Examine the CloudWatch logs for detailed error messages
   - Look for timeout issues or permission-related errors

## Conclusion

After completing these verification steps, you should have confirmed that:

1. The Lambda function is deployed and configured correctly
2. The API Gateway is properly integrated with the Lambda function
3. The S3 bucket is created and accessible
4. The Lambda function can successfully scrape stock data and store it in S3
5. The API Gateway endpoint returns the expected response format

If all verification steps pass, the Stock Price Scraper Lambda function is ready for use!

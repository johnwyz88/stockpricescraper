
set -e

STACK_NAME="stock-price-scraper"
ENVIRONMENT="dev"
S3_BUCKET_NAME="stock-data-bucket-$(date +%s)"
REGION="us-east-1"

while [[ $# -gt 0 ]]; do
  case $1 in
    --stack-name)
      STACK_NAME="$2"
      shift 2
      ;;
    --environment)
      ENVIRONMENT="$2"
      shift 2
      ;;
    --s3-bucket)
      S3_BUCKET_NAME="$2"
      shift 2
      ;;
    --region)
      REGION="$2"
      shift 2
      ;;
    --api-key)
      SCRAPER_API_KEY="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [ -z "$SCRAPER_API_KEY" ]; then
  echo "Error: ScraperAPI key is required. Use --api-key parameter."
  exit 1
fi

echo "Creating deployment package..."
cd "$(dirname "$0")/../scraper"
pip install -r requirements.txt -t ./package
cp *.py ./package/
cd ./package
zip -r ../deployment-package.zip .
cd ..
rm -rf ./package

echo "Deploying Lambda function using AWS SAM..."
cd "$(dirname "$0")"
sam deploy \
  --template-file template.yaml \
  --stack-name "$STACK_NAME" \
  --parameter-overrides \
    Environment="$ENVIRONMENT" \
    ScraperApiKey="$SCRAPER_API_KEY" \
    S3BucketName="$S3_BUCKET_NAME" \
  --capabilities CAPABILITY_IAM \
  --region "$REGION" \
  --no-fail-on-empty-changeset

echo "Deployment completed successfully!"
echo "API Gateway endpoint can be found in the CloudFormation stack outputs."

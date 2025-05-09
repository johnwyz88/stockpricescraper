
set -e

STACK_NAME="stock-price-scraper"
ENVIRONMENT="dev"
S3_BUCKET_NAME="stock-price-scraper-1746765924"
REGION="us-west-2"

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
  echo "No ScraperAPI key provided. Using direct HTTP requests instead."
  SCRAPER_API_KEY=""
fi

echo "Creating minimal deployment package without pandas..."
cd "$(dirname "$0")/../scraper"
mkdir -p ./minimal_package
pip install requests==2.31.0 beautifulsoup4==4.12.2 boto3==1.28.38 -t ./minimal_package
cp *.py ./minimal_package/
cd ./minimal_package
zip -r ../lambda_minimal.zip .
cd ..
rm -rf ./minimal_package

echo "Deploying Lambda function using AWS SAM..."
cd "$(dirname "$0")"
if [ ! -f "template.yaml" ]; then
  echo "Template file not found at $(pwd)/template.yaml"
  echo "Creating a simple deployment package instead..."
  
  cd ../scraper
  mkdir -p ./lambda_package
  cp *.py ./lambda_package/
  cd ./lambda_package
  pip install requests beautifulsoup4 boto3 -t .
  zip -r ../lambda_deployment.zip .
  cd ..
  
  echo "Deploying using AWS CLI..."
  aws lambda update-function-code \
    --function-name stock-scraper-$ENVIRONMENT \
    --zip-file fileb://lambda_deployment.zip \
    --region $REGION
  
  rm -rf ./lambda_package
else
  sam deploy \
    --template-file template.yaml \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
      "ParameterKey=Environment,ParameterValue=$ENVIRONMENT ParameterKey=ScraperApiKey,ParameterValue=$SCRAPER_API_KEY ParameterKey=S3BucketName,ParameterValue=$S3_BUCKET_NAME" \
    --capabilities CAPABILITY_IAM \
    --region "$REGION" \
    --no-fail-on-empty-changeset
fi

echo "Deployment completed successfully!"
echo "API Gateway endpoint can be found in the CloudFormation stack outputs."

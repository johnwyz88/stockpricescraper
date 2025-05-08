"""
Script to test the Lambda function locally
"""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scraper"))

from lambda_handler import lambda_handler

def test_lambda_locally():
    """
    Test the Lambda function locally with sample event data
    """
    print("Testing Lambda function locally...")
    
    event = {
        'body': json.dumps({
            'stock_symbols': ['nike', 'coca-cola-co', 'microsoft-corp'],
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
            'output_format': 'json'
        })
    }
    
    os.environ['SCRAPER_API_KEY'] = 'test_api_key'
    os.environ['S3_BUCKET_NAME'] = 'test-stock-data-bucket'
    os.environ['AWS_REGION'] = 'us-east-1'
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ['TEMP_OUTPUT_DIR'] = temp_dir
        
        try:
            response = lambda_handler(event, None)
            
            print("\nLambda function response:")
            print(json.dumps(response, indent=2))
            
            if response['statusCode'] == 200:
                print("\nLambda function executed successfully!")
                return True
            else:
                print(f"\nLambda function returned error: {response['body']}")
                return False
        except Exception as e:
            print(f"\nError executing Lambda function: {e}")
            return False

if __name__ == "__main__":
    test_result = test_lambda_locally()
    sys.exit(0 if test_result else 1)

import json
import logging
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock

from scraper import StockScraper
from data_processor import DataProcessor
from s3_manager import S3Manager

try:
    from mock_data import MOCK_STOCK_DATA
except ImportError:
    MOCK_STOCK_DATA = {}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'stock-data-bucket')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
LOCAL_TESTING = os.environ.get('LOCAL_TESTING', 'false').lower() == 'true'
TEMP_OUTPUT_DIR = os.environ.get('TEMP_OUTPUT_DIR', '/tmp')

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event (dict): Lambda event data
        context (object): Lambda context
        
    Returns:
        dict: Response with status and data
    """
    logger.info("Starting stock data scraper Lambda function")
    logger.info(f"Event: {json.dumps(event)}")
    
    try:
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        stock_symbols = body.get('stock_symbols', [])
        start_date = body.get('start_date')
        end_date = body.get('end_date')
        output_format = body.get('output_format', 'json').lower()
        
        if not stock_symbols:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'No stock symbols provided'
                })
            }
        
        scraper = StockScraper(api_key=SCRAPER_API_KEY)
        processor = DataProcessor()
        s3_manager = S3Manager(bucket_name=S3_BUCKET_NAME, region_name=AWS_REGION)
        
        if LOCAL_TESTING:
            logger.info("Using mock data for local testing")
            stock_data = []
            for symbol in stock_symbols:
                if symbol in MOCK_STOCK_DATA:
                    stock_data.append(MOCK_STOCK_DATA[symbol])
                else:
                    stock_data.append({
                        'symbol': symbol,
                        'company_name': f'Mock Company {symbol.capitalize()}',
                        'current_price': '100.00',
                        'price_change': '+1.00',
                        'timestamp': datetime.now().isoformat()
                    })
        else:
            stock_data = scraper.scrape_multiple_stocks(stock_symbols)
        
        processed_data = processor.process_data(stock_data, start_date, end_date)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        symbols_str = '-'.join(stock_symbols)
        filename = f"stock_data_{symbols_str}_{timestamp}"
        
        if LOCAL_TESTING:
            logger.info(f"Saving data locally to {TEMP_OUTPUT_DIR}/{filename}.{output_format}")
            local_path = os.path.join(TEMP_OUTPUT_DIR, f"{filename}.{output_format}")
            
            if output_format == 'json':
                with open(local_path, 'w') as f:
                    json.dump(processed_data, f, indent=2)
            else:
                if output_format == 'csv':
                    scraper.save_to_csv(processed_data, local_path)
                
            s3_uri = f"file://{local_path}"
            presigned_url = f"file://{local_path}"
        else:
            s3_key = f"data/{filename}.{output_format}"
            s3_uri = s3_manager.upload_data(processed_data, s3_key, file_format=output_format)
            presigned_url = s3_manager.generate_presigned_url(s3_key, expiration=3600)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Stock data scraped successfully',
                'data': {
                    's3_uri': s3_uri,
                    'download_url': presigned_url,
                    'expiration': '1 hour',
                    'stock_symbols': stock_symbols,
                    'start_date': start_date,
                    'end_date': end_date,
                    'output_format': output_format
                }
            })
        }
    
    except Exception as e:
        logger.error(f"Error in Lambda function: {e}", exc_info=True)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f"An error occurred: {str(e)}"
            })
        }


if __name__ == "__main__":
    os.environ['LOCAL_TESTING'] = 'true'
    os.environ['TEMP_OUTPUT_DIR'] = tempfile.gettempdir()
    
    test_event = {
        'body': json.dumps({
            'stock_symbols': ['nike', 'coca-cola-co', 'microsoft-corp'],
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
            'output_format': 'json'
        })
    }
    
    response = lambda_handler(test_event, None)
    
    print(json.dumps(response, indent=2))
    
    response_body = json.loads(response['body'])
    local_file_path = response_body['data']['s3_uri'].replace('file://', '')
    
    print(f"\nSaved data to: {local_file_path}")
    
    if os.path.exists(local_file_path):
        print("\nOutput file contents (first 200 chars):")
        with open(local_file_path, 'r') as f:
            content = f.read()
            print(content[:200] + "..." if len(content) > 200 else content)

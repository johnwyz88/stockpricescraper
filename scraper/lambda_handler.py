import json
import logging
import os
import tempfile
from datetime import datetime

from scraper import StockScraper
from data_processor import DataProcessor
from s3_manager import S3Manager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCRAPER_API_KEY = os.environ.get('SCRAPER_API_KEY')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'stock-data-bucket')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

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
        
        stock_data = scraper.scrape_multiple_stocks(stock_symbols)
        
        processed_data = processor.process_data(stock_data, start_date, end_date)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        symbols_str = '-'.join(stock_symbols)
        filename = f"stock_data_{symbols_str}_{timestamp}"
        
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

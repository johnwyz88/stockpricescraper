"""
Simplified script to test the Lambda function locally without pandas dependency
"""
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

MOCK_STOCK_DATA = {
    'nike': {
        'symbol': 'nike',
        'company_name': 'Nike Inc',
        'current_price': '98.76',
        'price_change': '+1.23',
        'timestamp': '2025-05-08T21:30:00'
    },
    'coca-cola-co': {
        'symbol': 'coca-cola-co',
        'company_name': 'The Coca-Cola Company',
        'current_price': '65.43',
        'price_change': '-0.32',
        'timestamp': '2025-05-08T21:30:00'
    },
    'microsoft-corp': {
        'symbol': 'microsoft-corp',
        'company_name': 'Microsoft Corporation',
        'current_price': '345.67',
        'price_change': '+5.67',
        'timestamp': '2025-05-08T21:30:00'
    }
}

class StockScraper:
    def __init__(self, api_key=None):
        self.api_key = api_key
    
    def scrape_multiple_stocks(self, symbols):
        return [MOCK_STOCK_DATA.get(symbol, {
            'symbol': symbol,
            'company_name': f'Mock Company {symbol.capitalize()}',
            'current_price': '100.00',
            'price_change': '+1.00',
            'timestamp': datetime.now().isoformat()
        }) for symbol in symbols]
    
    def save_to_csv(self, data, filename):
        with open(filename, 'w') as f:
            f.write("symbol,company_name,current_price,price_change,timestamp\n")
            for item in data:
                f.write(f"{item['symbol']},{item['company_name']},{item['current_price']},{item['price_change']},{item['timestamp']}\n")

class DataProcessor:
    def process_data(self, data, start_date=None, end_date=None):
        for item in data:
            item['processed_at'] = datetime.now().isoformat()
            if 'current_price' in item and isinstance(item['current_price'], str):
                try:
                    item['current_price'] = float(item['current_price'].replace('$', '').replace(',', ''))
                except ValueError:
                    pass
            if 'price_change' in item and isinstance(item['price_change'], str):
                try:
                    item['price_change'] = float(item['price_change'].replace('+', ''))
                except ValueError:
                    pass
        return data

class S3Manager:
    def __init__(self, bucket_name=None, region_name=None):
        self.bucket_name = bucket_name
        self.region_name = region_name
    
    def upload_data(self, data, key, file_format='json'):
        local_path = os.path.join(tempfile.gettempdir(), os.path.basename(key))
        if file_format == 'json':
            with open(local_path, 'w') as f:
                json.dump(data, f, indent=2)
        return f"s3://{self.bucket_name}/{key}"
    
    def generate_presigned_url(self, key, expiration=3600):
        return f"https://{self.bucket_name}.s3.amazonaws.com/{key}?expiration={expiration}"

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event (dict): Lambda event data
        context (object): Lambda context
        
    Returns:
        dict: Response with status and data
    """
    print("Starting stock data scraper Lambda function")
    print(f"Event: {json.dumps(event)}")
    
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
        
        scraper = StockScraper(api_key="test_api_key")
        processor = DataProcessor()
        s3_manager = S3Manager(bucket_name="test-stock-data-bucket", region_name="us-east-1")
        
        print("Using mock data for local testing")
        stock_data = scraper.scrape_multiple_stocks(stock_symbols)
        
        processed_data = processor.process_data(stock_data, start_date, end_date)
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        symbols_str = '-'.join(stock_symbols)
        filename = f"stock_data_{symbols_str}_{timestamp}"
        
        temp_dir = tempfile.gettempdir()
        print(f"Saving data locally to {temp_dir}/{filename}.{output_format}")
        local_path = os.path.join(temp_dir, f"{filename}.{output_format}")
        
        if output_format == 'json':
            with open(local_path, 'w') as f:
                json.dump(processed_data, f, indent=2)
        else:
            if output_format == 'csv':
                scraper.save_to_csv(processed_data, local_path)
            
        s3_uri = f"s3://test-stock-data-bucket/data/{filename}.{output_format}"
        presigned_url = f"https://test-stock-data-bucket.s3.amazonaws.com/data/{filename}.{output_format}?expiration=3600"
        
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
                    'output_format': output_format,
                    'local_file': local_path
                }
            })
        }
    
    except Exception as e:
        print(f"Error in Lambda function: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f"An error occurred: {str(e)}"
            })
        }

def test_lambda_locally():
    """
    Test the Lambda function locally with sample event data
    """
    print("Testing Lambda function locally...")
    
    global event
    
    try:
        response = lambda_handler(event, None)
        
        print("\nLambda function response:")
        print(json.dumps(response, indent=2))
        
        if response['statusCode'] == 200:
            response_body = json.loads(response['body'])
            local_file = response_body['data'].get('local_file')
            
            if local_file and os.path.exists(local_file):
                print(f"\nOutput file saved to: {local_file}")
                print("\nOutput file contents (first 200 chars):")
                with open(local_file, 'r') as f:
                    content = f.read()
                    print(content[:200] + "..." if len(content) > 200 else content)
            
            print("\nLambda function executed successfully!")
            return True
        else:
            print(f"\nLambda function returned error: {response['body']}")
            return False
    except Exception as e:
        print(f"\nError executing Lambda function: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Test Lambda function locally')
    parser.add_argument('--output-format', type=str, default='json', choices=['json', 'csv'],
                        help='Output format (json or csv)')
    parser.add_argument('--stock-symbols', type=str, default='nike,coca-cola-co,microsoft-corp',
                        help='Comma-separated list of stock symbols')
    parser.add_argument('--start-date', type=str, default='2023-01-01',
                        help='Start date for stock data (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default='2023-01-31',
                        help='End date for stock data (YYYY-MM-DD)')
    args = parser.parse_args()
    
    global event
    event = {
        'body': json.dumps({
            'stock_symbols': args.stock_symbols.split(','),
            'start_date': args.start_date,
            'end_date': args.end_date,
            'output_format': args.output_format
        })
    }
    
    test_result = test_lambda_locally()
    sys.exit(0 if test_result else 1)

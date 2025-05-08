import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scraper import StockScraper
from data_processor import DataProcessor
from s3_manager import S3Manager
from lambda_handler import lambda_handler

class TestStockScraper(unittest.TestCase):
    """
    Test cases for the StockScraper class
    """
    
    @patch('scraper.requests.get')
    def test_get_page_content(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<html><body>Test HTML</body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        scraper = StockScraper()
        
        result = scraper._get_page_content('https://example.com')
        
        self.assertEqual(result, '<html><body>Test HTML</body></html>')
        mock_get.assert_called_once()
    
    @patch('scraper.StockScraper._get_page_content')
    @patch('scraper.BeautifulSoup')
    def test_scrape_stock_data(self, mock_bs, mock_get_content):
        mock_get_content.return_value = '<html><body>Test HTML</body></html>'
        
        mock_soup = MagicMock()
        mock_bs.return_value = mock_soup
        
        mock_h1 = MagicMock()
        mock_h1.text = 'Test Company'
        mock_soup.find.return_value = mock_h1
        
        mock_div = MagicMock()
        mock_spans = [MagicMock(), MagicMock(), MagicMock()]
        mock_spans[0].text = '100.00'
        mock_spans[2].text = '+2.50'
        mock_div.find_all.return_value = mock_spans
        mock_soup.find.return_value = mock_div
        
        scraper = StockScraper()
        
        result = scraper.scrape_stock_data('test-stock')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['symbol'], 'test-stock')
        self.assertEqual(result[0]['company_name'], 'Test Company')
        self.assertEqual(result[0]['current_price'], '100.00')
        self.assertEqual(result[0]['price_change'], '+2.50')


class TestDataProcessor(unittest.TestCase):
    """
    Test cases for the DataProcessor class
    """
    
    def test_clean_price(self):
        processor = DataProcessor()
        
        self.assertEqual(processor._clean_price('$100.00'), 100.00)
        self.assertEqual(processor._clean_price('$1,234.56'), 1234.56)
        self.assertEqual(processor._clean_price('+10.5%'), 10.5)
        self.assertEqual(processor._clean_price('-5.25'), -5.25)
        self.assertEqual(processor._clean_price('(2.75)'), -2.75)
        self.assertIsNone(processor._clean_price('N/A'))
        self.assertIsNone(processor._clean_price(''))
    
    def test_clean_data(self):
        processor = DataProcessor()
        
        test_data = [
            {
                'symbol': 'AAPL',
                'company_name': 'Apple Inc.',
                'current_price': '$150.25',
                'price_change': '+2.75',
                'timestamp': '2023-01-01T12:00:00'
            }
        ]
        
        result = processor.clean_data(test_data)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['symbol'], 'AAPL')
        self.assertEqual(result[0]['company_name'], 'Apple Inc.')
        self.assertEqual(result[0]['current_price'], 150.25)
        self.assertEqual(result[0]['price_change'], 2.75)
        self.assertEqual(result[0]['timestamp'], '2023-01-01T12:00:00')
        self.assertIn('processed_at', result[0])


class TestS3Manager(unittest.TestCase):
    """
    Test cases for the S3Manager class
    """
    
    @patch('s3_manager.boto3.client')
    def test_ensure_bucket_exists_success(self, mock_boto3_client):
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3
        
        mock_s3.head_bucket.return_value = {}
        
        s3_manager = S3Manager('test-bucket')
        
        mock_s3.head_bucket.assert_called_once_with(Bucket='test-bucket')
        mock_s3.create_bucket.assert_not_called()
    
    @patch('s3_manager.boto3.client')
    def test_upload_data_json(self, mock_boto3_client):
        mock_s3 = MagicMock()
        mock_boto3_client.return_value = mock_s3
        
        mock_s3.head_bucket.return_value = {}
        
        s3_manager = S3Manager('test-bucket')
        
        test_data = {'key': 'value'}
        
        result = s3_manager.upload_data(test_data, 'test-key.json', 'json')
        
        self.assertEqual(result, 's3://test-bucket/test-key.json')
        mock_s3.put_object.assert_called_once()


class TestLambdaHandler(unittest.TestCase):
    """
    Test cases for the Lambda handler
    """
    
    @patch('lambda_handler.StockScraper')
    @patch('lambda_handler.DataProcessor')
    @patch('lambda_handler.S3Manager')
    def test_lambda_handler_success(self, mock_s3_manager, mock_processor, mock_scraper):
        mock_scraper_instance = MagicMock()
        mock_scraper.return_value = mock_scraper_instance
        mock_scraper_instance.scrape_multiple_stocks.return_value = [{'symbol': 'TEST'}]
        
        mock_processor_instance = MagicMock()
        mock_processor.return_value = mock_processor_instance
        mock_processor_instance.process_data.return_value = [{'symbol': 'TEST', 'processed': True}]
        
        mock_s3_instance = MagicMock()
        mock_s3_manager.return_value = mock_s3_instance
        mock_s3_instance.upload_data.return_value = 's3://test-bucket/test-key.json'
        mock_s3_instance.generate_presigned_url.return_value = 'https://presigned-url.example.com'
        
        test_event = {
            'body': json.dumps({
                'stock_symbols': ['test-stock'],
                'start_date': '2023-01-01',
                'end_date': '2023-01-31',
                'output_format': 'json'
            })
        }
        
        response = lambda_handler(test_event, None)
        
        self.assertEqual(response['statusCode'], 200)
        response_body = json.loads(response['body'])
        self.assertEqual(response_body['message'], 'Stock data scraped successfully')
        self.assertEqual(response_body['data']['stock_symbols'], ['test-stock'])
        self.assertEqual(response_body['data']['s3_uri'], 's3://test-bucket/test-key.json')
        self.assertEqual(response_body['data']['download_url'], 'https://presigned-url.example.com')


if __name__ == '__main__':
    unittest.main()

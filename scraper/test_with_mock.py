import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scraper import StockScraper
from data_processor import DataProcessor
from mock_data import MOCK_STOCK_DATA

class TestScraperWithMockData(unittest.TestCase):
    """
    Test cases for the StockScraper class using mock data
    """
    
    def test_scrape_stock_data_with_mock(self):
        """Test scraping stock data with mock data"""
        scraper = StockScraper()
        
        for symbol, expected_data in MOCK_STOCK_DATA.items():
            with patch.object(scraper, '_get_page_content', return_value='<html><body>Mock HTML</body></html>'):
                with patch.object(scraper, 'scrape_stock_data', return_value=[expected_data]):
                    result = scraper.scrape_stock_data(symbol)
                    
                    self.assertEqual(len(result), 1)
                    self.assertEqual(result[0]['symbol'], expected_data['symbol'])
                    self.assertEqual(result[0]['company_name'], expected_data['company_name'])
                    self.assertEqual(result[0]['current_price'], expected_data['current_price'])
                    self.assertEqual(result[0]['price_change'], expected_data['price_change'])
    
    def test_data_processor_with_mock(self):
        """Test data processor with mock data"""
        processor = DataProcessor()
        
        mock_data_list = list(MOCK_STOCK_DATA.values())
        
        cleaned_data = processor.clean_data(mock_data_list)
        
        self.assertEqual(len(cleaned_data), len(mock_data_list))
        for i, item in enumerate(cleaned_data):
            self.assertIn('processed_at', item)
            self.assertIsNotNone(item['current_price'])
            self.assertIsNotNone(item['price_change'])
    
    def test_save_to_json(self):
        """Test saving data to JSON"""
        scraper = StockScraper()
        
        mock_data_list = list(MOCK_STOCK_DATA.values())
        
        temp_file = 'temp_test_data.json'
        
        try:
            scraper.save_to_json(mock_data_list, temp_file)
            
            self.assertTrue(os.path.exists(temp_file))
            
            with open(temp_file, 'r') as f:
                saved_data = json.load(f)
            
            self.assertEqual(len(saved_data), len(mock_data_list))
            for i, item in enumerate(saved_data):
                self.assertEqual(item['symbol'], mock_data_list[i]['symbol'])
                self.assertEqual(item['company_name'], mock_data_list[i]['company_name'])
        
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == '__main__':
    unittest.main()

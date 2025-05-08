import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from mock_data import MOCK_STOCK_DATA

class TestScraperComponents(unittest.TestCase):
    """
    Test cases for the scraper components without pandas dependency
    """
    
    def test_mock_data_structure(self):
        """Test the structure of mock data"""
        for symbol, data in MOCK_STOCK_DATA.items():
            self.assertIn('symbol', data)
            self.assertIn('company_name', data)
            self.assertIn('current_price', data)
            self.assertIn('price_change', data)
            self.assertIn('timestamp', data)
    
    def test_price_cleaning(self):
        """Test price cleaning function"""
        test_cases = [
            ('$123.45', 123.45),
            ('$1,234.56', 1234.56),
            ('+2.75', 2.75),
            ('-1.25', -1.25),
            ('(0.5)', -0.5),
            ('N/A', None)
        ]
        
        for price_str, expected in test_cases:
            result = self._clean_price(price_str)
            self.assertEqual(result, expected)
    
    def _clean_price(self, price_str):
        """
        Clean price string by removing currency symbols, commas, etc.
        
        Args:
            price_str (str): Price string to clean
            
        Returns:
            float: Cleaned price as float, or None if invalid
        """
        if not price_str or price_str == "N/A":
            return None
        
        try:
            cleaned = price_str.replace('$', '').replace(',', '').replace(' ', '')
            
            if '%' in cleaned:
                cleaned = cleaned.replace('%', '')
            
            if '(' in cleaned and ')' in cleaned:
                cleaned = cleaned.replace('(', '-').replace(')', '')
            
            return float(cleaned)
        except ValueError:
            return None
    
    def test_json_serialization(self):
        """Test JSON serialization of stock data"""
        mock_data_list = list(MOCK_STOCK_DATA.values())
        
        temp_file = 'temp_test_data.json'
        
        try:
            with open(temp_file, 'w') as f:
                json.dump(mock_data_list, f, indent=4)
            
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

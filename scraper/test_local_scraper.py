import json
import os
from datetime import datetime
from scraper import StockScraper
from data_processor import DataProcessor
from s3_manager import S3Manager
from mock_data import MOCK_STOCK_DATA

# Set environment variables for local testing
os.environ['LOCAL_TESTING'] = 'true'
os.environ['S3_BUCKET_NAME'] = 'stock-price-scraper-1746765924'

def test_scraper_without_api_key():
    """Test the scraper without using an API key"""
    print("Testing scraper without API key...")
    
    # Initialize scraper without API key
    scraper = StockScraper(api_key=None)
    
    # Test with a few stock symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    for symbol in symbols:
        print(f"\nScraping data for {symbol}...")
        try:
            data = scraper.scrape_stock_data(symbol)
            print(f"Success! Data: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"Error scraping {symbol}: {e}")
    
    # Test scraping multiple stocks at once
    print("\nScraping multiple stocks at once...")
    try:
        data = scraper.scrape_multiple_stocks(symbols)
        print(f"Success! Data: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Error scraping multiple stocks: {e}")

def test_data_processor():
    """Test the data processor with date filtering"""
    print("\nTesting data processor with date filtering...")
    
    # Create sample data with different dates
    sample_data = [
        {
            'symbol': 'AAPL',
            'company_name': 'Apple Inc.',
            'current_price': '175.50',
            'price_change': '+2.30',
            'timestamp': '2023-01-15T00:00:00'
        },
        {
            'symbol': 'AAPL',
            'company_name': 'Apple Inc.',
            'current_price': '180.10',
            'price_change': '+4.60',
            'timestamp': '2023-02-20T00:00:00'
        },
        {
            'symbol': 'AAPL',
            'company_name': 'Apple Inc.',
            'current_price': '165.30',
            'price_change': '-14.80',
            'timestamp': '2023-03-10T00:00:00'
        }
    ]
    
    processor = DataProcessor()
    
    # Test with no date filtering
    filtered_data = processor.process_data(sample_data)
    print(f"No date filtering: {len(filtered_data)} items")
    
    # Test with start date only
    filtered_data = processor.process_data(sample_data, start_date='2023-02-01')
    print(f"Start date only: {len(filtered_data)} items")
    
    # Test with end date only
    filtered_data = processor.process_data(sample_data, end_date='2023-02-25')
    print(f"End date only: {len(filtered_data)} items")
    
    # Test with both start and end date
    filtered_data = processor.process_data(sample_data, start_date='2023-01-20', end_date='2023-03-01')
    print(f"Start and end date: {len(filtered_data)} items")

if __name__ == "__main__":
    print("=== STOCK SCRAPER FUNCTIONALITY TEST ===")
    test_scraper_without_api_key()
    test_data_processor()
    print("\n=== TEST COMPLETED ===")

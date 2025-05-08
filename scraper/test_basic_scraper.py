import requests
from bs4 import BeautifulSoup
from scraper import StockScraper

def test_scraper():
    """
    Test the basic functionality of the StockScraper class
    """
    scraper = StockScraper()
    
    stocks = ['nike', 'coca-cola-co', 'microsoft-corp']
    
    print('Testing scraper with stock symbol:', stocks[0])
    try:
        data = scraper.scrape_stock_data(stocks[0])
        print('Scraped data:')
        for key, value in data[0].items():
            print(f"  {key}: {value}")
        
        required_fields = ['symbol', 'company_name', 'current_price', 'price_change', 'timestamp']
        missing_fields = [field for field in required_fields if field not in data[0]]
        
        if missing_fields:
            print(f"ERROR: Missing required fields: {missing_fields}")
            return False
        else:
            print("SUCCESS: All required fields are present")
            return True
    except Exception as e:
        print(f"ERROR: Failed to scrape data: {e}")
        return False

if __name__ == "__main__":
    test_result = test_scraper()
    print(f"\nTest {'PASSED' if test_result else 'FAILED'}")

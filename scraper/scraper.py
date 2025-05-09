import requests
from bs4 import BeautifulSoup
import csv
import json
import logging
import time
import random
from urllib.parse import urlencode
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockScraper:
    """
    A class to scrape historical stock data from investing.com
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the scraper with optional ScraperAPI key
        
        Args:
            api_key (str, optional): ScraperAPI key for handling anti-scraping measures
        """
        self.api_key = api_key
        self.base_url = 'https://www.investing.com/equities/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
    
    def _get_page_content(self, url, max_retries=3, retry_delay=2):
        """
        Get the page content using direct requests with retry logic and rotating user agents
        
        Args:
            url (str): URL to scrape
            max_retries (int): Maximum number of retry attempts
            retry_delay (int): Base delay between retries in seconds
            
        Returns:
            str: HTML content of the page
        """
        retries = 0
        
        while retries < max_retries:
            try:
                # If API key is provided, use ScraperAPI
                if self.api_key:
                    params = {
                        'api_key': self.api_key,
                        'url': url
                    }
                    response = requests.get('http://api.scraperapi.com/', params=urlencode(params))
                else:
                    current_headers = self.headers.copy()
                    current_headers['User-Agent'] = random.choice(self.user_agents)
                    
                    time.sleep(random.uniform(0.5, 1.5))
                    
                    response = requests.get(url, headers=current_headers, timeout=10)
                
                response.raise_for_status()
                return response.text
                
            except requests.exceptions.RequestException as e:
                retries += 1
                logger.warning(f"Attempt {retries}/{max_retries} failed for URL {url}: {e}")
                
                if retries >= max_retries:
                    logger.error(f"Max retries reached for URL {url}")
                    raise
                
                sleep_time = retry_delay * (2 ** (retries - 1)) + random.uniform(0, 1)
                logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
    
    def scrape_stock_data(self, stock_symbol, start_date=None, end_date=None):
        """
        Scrape stock data for a given symbol and date range
        
        Args:
            stock_symbol (str): Stock symbol or URL suffix on investing.com
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            list: List of dictionaries containing stock data
        """
        url = f"{self.base_url}{stock_symbol}"
        logger.info(f"Scraping stock data from: {url}")
        
        html_content = self._get_page_content(url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            company_name = soup.find('h1', {'class': 'text-2xl font-semibold instrument-header_title__GTWDv mobile:mb-2'}).text.strip()
            price_div = soup.find('div', {'class': 'instrument-price_instrument-price__3uw25 flex items-end flex-wrap font-bold'})
            
            if price_div:
                spans = price_div.find_all('span')
                current_price = spans[0].text.strip() if len(spans) > 0 else "N/A"
                price_change = spans[2].text.strip() if len(spans) > 2 else "N/A"
            else:
                current_price = "N/A"
                price_change = "N/A"
            
            
            stock_data = {
                'symbol': stock_symbol,
                'company_name': company_name,
                'current_price': current_price,
                'price_change': price_change,
                'timestamp': datetime.now().isoformat(),
            }
            
            logger.info(f"Successfully scraped data for {company_name}")
            return [stock_data]
            
        except Exception as e:
            logger.error(f"Error parsing stock data: {e}")
            raise
    
    def scrape_multiple_stocks(self, stock_symbols):
        """
        Scrape data for multiple stock symbols
        
        Args:
            stock_symbols (list): List of stock symbols or URL suffixes
            
        Returns:
            list: List of dictionaries containing stock data for all symbols
        """
        all_stock_data = []
        
        for symbol in stock_symbols:
            try:
                stock_data = self.scrape_stock_data(symbol)
                all_stock_data.extend(stock_data)
            except Exception as e:
                logger.error(f"Failed to scrape data for {symbol}: {e}")
                continue
        
        return all_stock_data
    
    def save_to_csv(self, stock_data, filename="stock_data.csv"):
        """
        Save stock data to a CSV file
        
        Args:
            stock_data (list): List of dictionaries containing stock data
            filename (str): Name of the output CSV file
        """
        if not stock_data:
            logger.warning("No stock data to save")
            return
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = stock_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for data in stock_data:
                    writer.writerow(data)
                
            logger.info(f"Stock data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
            raise
    
    def save_to_json(self, stock_data, filename="stock_data.json"):
        """
        Save stock data to a JSON file
        
        Args:
            stock_data (list): List of dictionaries containing stock data
            filename (str): Name of the output JSON file
        """
        if not stock_data:
            logger.warning("No stock data to save")
            return
        
        try:
            with open(filename, 'w') as jsonfile:
                json.dump(stock_data, jsonfile, indent=4)
                
            logger.info(f"Stock data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            raise


if __name__ == "__main__":
    scraper = StockScraper(api_key=None)
    
    stocks = ['nike', 'coca-cola-co', 'microsoft-corp']
    
    data = scraper.scrape_multiple_stocks(stocks)
    
    scraper.save_to_csv(data)
    scraper.save_to_json(data)

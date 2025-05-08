import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataProcessor:
    """
    A class to process and transform scraped stock data
    """
    
    def __init__(self):
        """
        Initialize the data processor
        """
        pass
    
    def clean_data(self, stock_data):
        """
        Clean and normalize the scraped stock data
        
        Args:
            stock_data (list): List of dictionaries containing stock data
            
        Returns:
            list: Cleaned list of dictionaries
        """
        cleaned_data = []
        
        for item in stock_data:
            try:
                cleaned_item = item.copy()
                
                if 'current_price' in cleaned_item:
                    cleaned_item['current_price'] = self._clean_price(cleaned_item['current_price'])
                
                if 'price_change' in cleaned_item:
                    cleaned_item['price_change'] = self._clean_price(cleaned_item['price_change'])
                
                cleaned_item['processed_at'] = datetime.now().isoformat()
                
                cleaned_data.append(cleaned_item)
            except Exception as e:
                logger.error(f"Error cleaning data item: {e}")
                logger.error(f"Problematic item: {item}")
                continue
        
        return cleaned_data
    
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
            logger.warning(f"Could not convert price string to float: {price_str}")
            return None
    
    def convert_to_dataframe(self, stock_data):
        """
        Convert list of dictionaries to pandas DataFrame
        
        Args:
            stock_data (list): List of dictionaries containing stock data
            
        Returns:
            pandas.DataFrame: DataFrame containing stock data
        """
        try:
            df = pd.DataFrame(stock_data)
            return df
        except Exception as e:
            logger.error(f"Error converting to DataFrame: {e}")
            raise
    
    def filter_by_date(self, df, start_date=None, end_date=None):
        """
        Filter DataFrame by date range
        
        Args:
            df (pandas.DataFrame): DataFrame containing stock data
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            pandas.DataFrame: Filtered DataFrame
        """
        if 'timestamp' not in df.columns:
            logger.warning("DataFrame does not contain timestamp column")
            return df
        
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            if start_date:
                start_date = pd.to_datetime(start_date)
                df = df[df['timestamp'] >= start_date]
            
            if end_date:
                end_date = pd.to_datetime(end_date)
                df = df[df['timestamp'] <= end_date]
            
            return df
        except Exception as e:
            logger.error(f"Error filtering by date: {e}")
            raise
    
    def calculate_metrics(self, df):
        """
        Calculate additional metrics from stock data
        
        Args:
            df (pandas.DataFrame): DataFrame containing stock data
            
        Returns:
            pandas.DataFrame: DataFrame with additional metrics
        """
        try:
            if 'current_price' in df.columns and 'price_change' in df.columns:
                df['percent_change'] = (df['price_change'] / (df['current_price'] - df['price_change'])) * 100
            
            return df
        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return df  # Return original DataFrame if calculation fails
    
    def process_data(self, stock_data, start_date=None, end_date=None):
        """
        Process stock data: clean, convert to DataFrame, filter, and calculate metrics
        
        Args:
            stock_data (list): List of dictionaries containing stock data
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            pandas.DataFrame: Processed DataFrame
        """
        try:
            cleaned_data = self.clean_data(stock_data)
            
            df = self.convert_to_dataframe(cleaned_data)
            
            df = self.filter_by_date(df, start_date, end_date)
            
            df = self.calculate_metrics(df)
            
            return df
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            raise


if __name__ == "__main__":
    sample_data = [
        {
            'symbol': 'AAPL',
            'company_name': 'Apple Inc.',
            'current_price': '$150.25',
            'price_change': '+2.75',
            'timestamp': '2023-01-01T12:00:00'
        },
        {
            'symbol': 'MSFT',
            'company_name': 'Microsoft Corporation',
            'current_price': '$245.50',
            'price_change': '-1.25',
            'timestamp': '2023-01-02T12:00:00'
        }
    ]
    
    processor = DataProcessor()
    
    processed_df = processor.process_data(sample_data)
    
    print(processed_df)

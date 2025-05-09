import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataProcessor:
    """
    A class to process stock data without pandas dependency
    """
    
    def __init__(self):
        """
        Initialize the data processor
        """
        pass
    
    def process_data(self, stock_data, start_date=None, end_date=None):
        """
        Process stock data based on date range without pandas
        
        Args:
            stock_data (list): List of dictionaries containing stock data
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            list: Filtered and processed stock data
        """
        if not stock_data:
            logger.warning("No stock data to process")
            return []
        
        # If no date filtering is needed, return the original data
        if not start_date and not end_date:
            return stock_data
        
        try:
            # Convert date strings to datetime objects if provided
            start_datetime = None
            end_datetime = None
            
            if start_date:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                logger.info(f"Filtering data from {start_date}")
            
            if end_date:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                logger.info(f"Filtering data to {end_date}")
            
            # Filter data based on date range
            filtered_data = []
            
            for item in stock_data:
                # Skip items without timestamp
                if 'timestamp' not in item:
                    filtered_data.append(item)
                    continue
                
                # Try to parse the timestamp
                try:
                    item_datetime = datetime.fromisoformat(item['timestamp'].split('T')[0])
                    
                    # Check if the item is within the date range
                    if start_datetime and item_datetime < start_datetime:
                        continue
                    
                    if end_datetime and item_datetime > end_datetime:
                        continue
                    
                    filtered_data.append(item)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Could not parse timestamp {item.get('timestamp')}: {e}")
                    # Include items with invalid timestamps
                    filtered_data.append(item)
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            # Return original data if processing fails
            return stock_data
    
    def aggregate_data(self, stock_data, aggregation='daily'):
        """
        Aggregate stock data by time period
        
        Args:
            stock_data (list): List of dictionaries containing stock data
            aggregation (str): Aggregation period ('daily', 'weekly', 'monthly')
            
        Returns:
            list: Aggregated stock data
        """
        # This is a placeholder for future implementation
        # For now, just return the original data
        return stock_data

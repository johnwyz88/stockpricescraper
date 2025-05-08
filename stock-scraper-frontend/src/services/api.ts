import axios from 'axios';

const API_URL = import.meta.env.VITE_API_ENDPOINT || 'https://api-gateway-url/dev/scrape';
const API_KEY = import.meta.env.VITE_API_KEY;

export interface ScrapeRequestParams {
  stockSymbols: string[];
  startDate: string;
  endDate: string;
  outputFormat: 'json' | 'csv';
}

export interface ScrapeResponse {
  s3_uri: string;
  download_url: string;
  expiration: string;
  stock_symbols: string[];
  start_date: string;
  end_date: string;
  output_format: string;
}

/**
 * API service for interacting with the stock scraper Lambda function
 */
const stockScraperApi = {
  /**
   * Scrape stock data based on provided parameters
   * @param params Stock scraping parameters
   * @returns Promise with scraping results
   */
  scrapeStockData: async (params: ScrapeRequestParams): Promise<ScrapeResponse> => {
    try {
      const response = await axios.post(
        API_URL,
        {
          stock_symbols: params.stockSymbols,
          start_date: params.startDate,
          end_date: params.endDate,
          output_format: params.outputFormat
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': API_KEY
          }
        }
      );
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response) {
          console.error('API Error Response:', error.response.data);
          throw new Error(
            error.response.data.message || 
            `API Error: ${error.response.status} - ${error.response.statusText}`
          );
        } else if (error.request) {
          console.error('API Request Error:', error.request);
          throw new Error('No response received from server. Please check your network connection.');
        } else {
          console.error('API Setup Error:', error.message);
          throw new Error(`Error setting up request: ${error.message}`);
        }
      }
      
      console.error('Unexpected error during API call:', error);
      throw new Error('An unexpected error occurred. Please try again later.');
    }
  },
  
  /**
   * Mock function for testing without a real API
   * @param params Stock scraping parameters
   * @returns Promise with mock scraping results
   */
  mockScrapeStockData: async (params: ScrapeRequestParams): Promise<ScrapeResponse> => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    return {
      s3_uri: `s3://stock-data-bucket/data/stock_data_${params.stockSymbols.join('_')}_${Date.now()}.${params.outputFormat}`,
      download_url: `https://stock-data-bucket.s3.amazonaws.com/data/stock_data_${params.stockSymbols.join('_')}_${Date.now()}.${params.outputFormat}`,
      expiration: "1 hour",
      stock_symbols: params.stockSymbols,
      start_date: params.startDate,
      end_date: params.endDate,
      output_format: params.outputFormat
    };
  }
};

export default stockScraperApi;

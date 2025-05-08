import { useState } from 'react';
import { StockScraperForm } from './components/stock-scraper/StockScraperForm';
import { StockScraperResults } from './components/stock-scraper/StockScraperResults';
import { PaymentRequired } from './components/stock-scraper/PaymentRequired';
import { StripePaymentForm } from './components/stock-scraper/StripePaymentForm';
import stockScraperApi, { ScrapeRequestParams } from './services/api';

interface FormValues {
  stockSymbols: string[];
  startDate: Date;
  endDate: Date;
  outputFormat: "json" | "csv";
}

interface StockData {
  s3_uri: string;
  download_url: string;
  expiration: string;
  stock_symbols: string[];
  start_date: string;
  end_date: string;
  output_format: string;
}

function App() {
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<StockData | null>(null);
  const [isPaid, setIsPaid] = useState(false);
  const [showPaymentForm, setShowPaymentForm] = useState(false);

  const handleSubmit = async (values: FormValues) => {
    setIsPending(true);
    setError(null);
    
    try {
      const requestParams: ScrapeRequestParams = {
        stockSymbols: values.stockSymbols,
        startDate: values.startDate.toISOString().split('T')[0],
        endDate: values.endDate.toISOString().split('T')[0],
        outputFormat: values.outputFormat
      };
      
      const apiResponse = import.meta.env.DEV 
        ? await stockScraperApi.mockScrapeStockData(requestParams)
        : await stockScraperApi.scrapeStockData(requestParams);
      
      setResult(apiResponse);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An error occurred while processing your request. Please try again.");
      }
      console.error(err);
    } finally {
      setIsPending(false);
    }
  };

  const handleProceedToPayment = () => {
    setShowPaymentForm(true);
  };

  const handlePaymentSuccess = () => {
    setIsPaid(true);
    setShowPaymentForm(false);
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b">
        <div className="container mx-auto py-4">
          <h1 className="text-2xl font-bold">Stock Price Scraper</h1>
        </div>
      </header>
      
      <main className="flex-1 container mx-auto py-8 px-4">
        {!isPaid ? (
          <PaymentRequired onProceedToPayment={handleProceedToPayment} />
        ) : (
          <>
            <StockScraperForm onSubmit={handleSubmit} isPending={isPending} />
            <StockScraperResults data={result} error={error} isLoading={isPending} />
          </>
        )}
        
        {showPaymentForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <StripePaymentForm 
              onPaymentSuccess={handlePaymentSuccess}
              onCancel={() => setShowPaymentForm(false)}
              amount={5.00}
            />
          </div>
        )}
      </main>
      
      <footer className="border-t">
        <div className="container mx-auto py-4 text-center text-sm text-muted-foreground">
          &copy; {new Date().getFullYear()} Stock Price Scraper. All rights reserved.
        </div>
      </footer>
    </div>
  );
}

export default App;

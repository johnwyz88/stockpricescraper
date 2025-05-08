import { useState } from 'react';
import { StockScraperForm } from './components/stock-scraper/StockScraperForm';
import { StockScraperResults } from './components/stock-scraper/StockScraperResults';
import { PaymentRequired } from './components/stock-scraper/PaymentRequired';

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
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResponse: StockData = {
        s3_uri: "s3://stock-data-bucket/data/stock_data_AAPL_MSFT_20250508123456.json",
        download_url: "https://example.com/download/stock_data_AAPL_MSFT_20250508123456.json",
        expiration: "1 hour",
        stock_symbols: values.stockSymbols,
        start_date: values.startDate.toISOString().split('T')[0],
        end_date: values.endDate.toISOString().split('T')[0],
        output_format: values.outputFormat
      };
      
      setResult(mockResponse);
    } catch (err) {
      setError("An error occurred while processing your request. Please try again.");
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
        
        {/* This is a placeholder for the Stripe payment form that will be implemented in step 5 */}
        {showPaymentForm && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
            <div className="bg-background rounded-lg p-6 max-w-md w-full">
              <h2 className="text-xl font-bold mb-4">Payment Form</h2>
              <p className="mb-4">This is a placeholder for the Stripe payment form that will be implemented in step 5.</p>
              <div className="flex justify-end gap-2">
                <button 
                  className="px-4 py-2 border rounded-md"
                  onClick={() => setShowPaymentForm(false)}
                >
                  Cancel
                </button>
                <button 
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-md"
                  onClick={handlePaymentSuccess}
                >
                  Simulate Payment
                </button>
              </div>
            </div>
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

import { Download, ExternalLink } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface StockData {
  s3_uri: string;
  download_url: string;
  expiration: string;
  stock_symbols: string[];
  start_date: string;
  end_date: string;
  output_format: string;
}

interface StockScraperResultsProps {
  data: StockData | null;
  error: string | null;
  isLoading: boolean;
}

export function StockScraperResults({ data, error, isLoading }: StockScraperResultsProps) {
  if (isLoading) {
    return (
      <Card className="w-full max-w-2xl mx-auto mt-8">
        <CardHeader>
          <CardTitle>Processing Request</CardTitle>
          <CardDescription>
            Please wait while we scrape the stock data...
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="w-full max-w-2xl mx-auto mt-8">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <Card className="w-full max-w-2xl mx-auto mt-8">
      <CardHeader>
        <CardTitle>Stock Data Results</CardTitle>
        <CardDescription>
          Your stock data has been successfully scraped and is ready for download.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h3 className="text-sm font-medium">Stock Symbols</h3>
            <p className="text-sm text-muted-foreground">
              {data.stock_symbols.join(", ")}
            </p>
          </div>
          <div>
            <h3 className="text-sm font-medium">Date Range</h3>
            <p className="text-sm text-muted-foreground">
              {data.start_date} to {data.end_date}
            </p>
          </div>
          <div>
            <h3 className="text-sm font-medium">Format</h3>
            <p className="text-sm text-muted-foreground uppercase">
              {data.output_format}
            </p>
          </div>
          <div>
            <h3 className="text-sm font-medium">Link Expiration</h3>
            <p className="text-sm text-muted-foreground">
              {data.expiration}
            </p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 mt-6">
          <Button className="flex-1" asChild>
            <a href={data.download_url} target="_blank" rel="noopener noreferrer">
              <Download className="mr-2 h-4 w-4" />
              Download Data
            </a>
          </Button>
          <Button variant="outline" className="flex-1" asChild>
            <a href={data.s3_uri} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="mr-2 h-4 w-4" />
              View S3 Location
            </a>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

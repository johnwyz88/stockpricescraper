import { LockKeyhole } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface PaymentRequiredProps {
  onProceedToPayment: () => void;
}

export function PaymentRequired({ onProceedToPayment }: PaymentRequiredProps) {
  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center">
          <LockKeyhole className="mr-2 h-5 w-5" />
          Payment Required
        </CardTitle>
        <CardDescription>
          Access to the stock data scraper requires a payment.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="bg-muted p-4 rounded-lg">
          <h3 className="font-medium mb-2">Stock Data Scraper Features:</h3>
          <ul className="list-disc pl-5 space-y-1">
            <li>Scrape historical stock price data from multiple sources</li>
            <li>Support for multiple stock symbols in a single request</li>
            <li>Customizable date ranges for targeted data collection</li>
            <li>Export data in JSON or CSV format</li>
            <li>Secure storage of results in Amazon S3</li>
            <li>Download links valid for 1 hour</li>
          </ul>
        </div>

        <div className="bg-primary/5 p-4 rounded-lg border border-primary/20">
          <h3 className="font-medium mb-2 text-primary">Pricing:</h3>
          <p className="text-2xl font-bold">$5.00 <span className="text-sm font-normal text-muted-foreground">per scraping job</span></p>
          <p className="text-sm text-muted-foreground mt-2">
            Each payment grants you access to run one scraping job with unlimited stock symbols.
          </p>
        </div>

        <Button 
          className="w-full mt-4" 
          onClick={onProceedToPayment}
        >
          Proceed to Payment
        </Button>
      </CardContent>
    </Card>
  );
}

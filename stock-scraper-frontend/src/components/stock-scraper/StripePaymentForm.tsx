import { useState } from "react";
import { loadStripe } from "@stripe/stripe-js";
import {
  CardElement,
  Elements,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "../../components/ui/card";
import { Alert, AlertDescription } from "../../components/ui/alert";

const stripePromise = loadStripe("pk_test_TYooMQauvdEDq54NiTphI7jx");

interface CheckoutFormProps {
  onPaymentSuccess: () => void;
  onCancel: () => void;
  amount: number;
}

const CheckoutForm = ({ onPaymentSuccess, onCancel, amount }: CheckoutFormProps) => {
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setProcessing(true);
    setError(null);

    const cardElement = elements.getElement(CardElement);

    if (!cardElement) {
      setError("Card element not found");
      setProcessing(false);
      return;
    }

    try {

      await new Promise(resolve => setTimeout(resolve, 1500));

      onPaymentSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unknown error occurred");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-4">
        <div className="border rounded-md p-3">
          <CardElement
            options={{
              style: {
                base: {
                  fontSize: '16px',
                  color: '#424770',
                  '::placeholder': {
                    color: '#aab7c4',
                  },
                },
                invalid: {
                  color: '#9e2146',
                },
              },
            }}
          />
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="bg-muted p-4 rounded-lg">
          <div className="flex justify-between items-center">
            <span>Total:</span>
            <span className="font-bold">${amount.toFixed(2)}</span>
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-2 mt-6">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={processing}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={!stripe || processing}
        >
          {processing ? "Processing..." : `Pay $${amount.toFixed(2)}`}
        </Button>
      </div>
    </form>
  );
};

interface StripePaymentFormProps {
  onPaymentSuccess: () => void;
  onCancel: () => void;
  amount: number;
}

export function StripePaymentForm({ onPaymentSuccess, onCancel, amount }: StripePaymentFormProps) {
  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>Payment Details</CardTitle>
        <CardDescription>
          Enter your card details to complete your purchase
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Elements stripe={stripePromise}>
          <CheckoutForm 
            onPaymentSuccess={onPaymentSuccess} 
            onCancel={onCancel}
            amount={amount}
          />
        </Elements>
      </CardContent>
      <CardFooter className="flex flex-col text-xs text-muted-foreground">
        <p>This is a test payment form. No actual charges will be made.</p>
        <p>You can use the test card number: 4242 4242 4242 4242</p>
        <p>Any future date, any 3 digits for CVC, and any 5 digits for postal code.</p>
      </CardFooter>
    </Card>
  );
}

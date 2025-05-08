import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import * as z from "zod";
import { CalendarIcon, Plus, Trash2 } from "lucide-react";
import { format } from "date-fns";

import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "../../components/ui/card";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "../../components/ui/form";
import { RadioGroup, RadioGroupItem } from "../../components/ui/radio-group";
import { Popover, PopoverContent, PopoverTrigger } from "../../components/ui/popover";
import { Calendar } from "../../components/ui/calendar";
import { cn } from "../../lib/utils";

const formSchema = z.object({
  stockSymbols: z.array(z.string().min(1, "Stock symbol is required")).min(1, "At least one stock symbol is required"),
  startDate: z.date({
    required_error: "Start date is required",
  }),
  endDate: z.date({
    required_error: "End date is required",
  }),
  outputFormat: z.enum(["json", "csv"], {
    required_error: "Please select an output format",
  }),
});

type FormValues = z.infer<typeof formSchema>;

interface StockScraperFormProps {
  onSubmit: (values: FormValues) => void;
  isPending: boolean;
}

export function StockScraperForm({ onSubmit, isPending }: StockScraperFormProps) {
  const [symbols, setSymbols] = useState<string[]>(['']);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      stockSymbols: [''],
      startDate: new Date(),
      endDate: new Date(),
      outputFormat: "json",
    },
  });

  const addSymbol = () => {
    const newSymbols = [...symbols, ''];
    setSymbols(newSymbols);
    form.setValue('stockSymbols', newSymbols);
  };

  const removeSymbol = (index: number) => {
    if (symbols.length > 1) {
      const newSymbols = symbols.filter((_, i) => i !== index);
      setSymbols(newSymbols);
      form.setValue('stockSymbols', newSymbols);
    }
  };

  const updateSymbol = (index: number, value: string) => {
    const newSymbols = [...symbols];
    newSymbols[index] = value;
    setSymbols(newSymbols);
    form.setValue('stockSymbols', newSymbols);
  };

  const handleSubmit = (values: FormValues) => {
    const filteredValues = {
      ...values,
      stockSymbols: values.stockSymbols.filter(symbol => symbol.trim() !== '')
    };
    
    onSubmit(filteredValues);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Stock Data Scraper</CardTitle>
        <CardDescription>
          Enter stock symbols and date range to scrape historical price data.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <div className="space-y-4">
              <FormLabel>Stock Symbols</FormLabel>
              <FormDescription>
                Enter the stock symbols you want to scrape (e.g., AAPL, MSFT, GOOGL)
              </FormDescription>
              
              {symbols.map((symbol, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Input
                    placeholder="Enter stock symbol"
                    value={symbol}
                    onChange={(e) => updateSymbol(index, e.target.value)}
                    className="flex-1"
                  />
                  {symbols.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={() => removeSymbol(index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
              
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="mt-2"
                onClick={addSymbol}
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Symbol
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="startDate"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Start Date</FormLabel>
                    <Popover>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            variant="outline"
                            className={cn(
                              "w-full pl-3 text-left font-normal",
                              !field.value && "text-muted-foreground"
                            )}
                          >
                            {field.value ? (
                              format(field.value, "PPP")
                            ) : (
                              <span>Pick a date</span>
                            )}
                            <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={field.value}
                          onSelect={field.onChange}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="endDate"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>End Date</FormLabel>
                    <Popover>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            variant="outline"
                            className={cn(
                              "w-full pl-3 text-left font-normal",
                              !field.value && "text-muted-foreground"
                            )}
                          >
                            {field.value ? (
                              format(field.value, "PPP")
                            ) : (
                              <span>Pick a date</span>
                            )}
                            <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={field.value}
                          onSelect={field.onChange}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="outputFormat"
              render={({ field }) => (
                <FormItem className="space-y-3">
                  <FormLabel>Output Format</FormLabel>
                  <FormControl>
                    <RadioGroup
                      onValueChange={field.onChange}
                      defaultValue={field.value}
                      className="flex space-x-4"
                    >
                      <FormItem className="flex items-center space-x-2 space-y-0">
                        <FormControl>
                          <RadioGroupItem value="json" />
                        </FormControl>
                        <FormLabel className="font-normal">JSON</FormLabel>
                      </FormItem>
                      <FormItem className="flex items-center space-x-2 space-y-0">
                        <FormControl>
                          <RadioGroupItem value="csv" />
                        </FormControl>
                        <FormLabel className="font-normal">CSV</FormLabel>
                      </FormItem>
                    </RadioGroup>
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <CardFooter className="px-0 pt-4">
              <Button type="submit" className="w-full" disabled={isPending}>
                {isPending ? "Processing..." : "Scrape Stock Data"}
              </Button>
            </CardFooter>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}

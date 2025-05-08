
resource "aws_api_gateway_rest_api" "stock_scraper_api" {
  name        = "stock-scraper-api-${var.environment}"
  description = "API Gateway for Stock Price Scraper"
}

resource "aws_api_gateway_resource" "scrape_resource" {
  rest_api_id = aws_api_gateway_rest_api.stock_scraper_api.id
  parent_id   = aws_api_gateway_rest_api.stock_scraper_api.root_resource_id
  path_part   = "scrape"
}

resource "aws_api_gateway_method" "scrape_post" {
  rest_api_id   = aws_api_gateway_rest_api.stock_scraper_api.id
  resource_id   = aws_api_gateway_resource.scrape_resource.id
  http_method   = "POST"
  authorization = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.stock_scraper_api.id
  resource_id             = aws_api_gateway_resource.scrape_resource.id
  http_method             = aws_api_gateway_method.scrape_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.stock_scraper.invoke_arn
}

resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id = aws_api_gateway_rest_api.stock_scraper_api.id
  resource_id = aws_api_gateway_resource.scrape_resource.id
  http_method = aws_api_gateway_method.scrape_post.http_method
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

resource "aws_api_gateway_method" "options_method" {
  rest_api_id   = aws_api_gateway_rest_api.stock_scraper_api.id
  resource_id   = aws_api_gateway_resource.scrape_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_method_response" "options_200" {
  rest_api_id = aws_api_gateway_rest_api.stock_scraper_api.id
  resource_id = aws_api_gateway_resource.scrape_resource.id
  http_method = aws_api_gateway_method.options_method.http_method
  status_code = "200"
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration" "options_integration" {
  rest_api_id = aws_api_gateway_rest_api.stock_scraper_api.id
  resource_id = aws_api_gateway_resource.scrape_resource.id
  http_method = aws_api_gateway_method.options_method.http_method
  type        = "MOCK"
  
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_integration_response" "options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.stock_scraper_api.id
  resource_id = aws_api_gateway_resource.scrape_resource.id
  http_method = aws_api_gateway_method.options_method.http_method
  status_code = aws_api_gateway_method_response.options_200.status_code
  
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'",
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda_integration,
    aws_api_gateway_integration.options_integration
  ]
  
  rest_api_id = aws_api_gateway_rest_api.stock_scraper_api.id
  stage_name  = var.environment
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.stock_scraper_api.id
  stage_name    = var.environment
}

resource "aws_api_gateway_api_key" "api_key" {
  name = "stock-scraper-api-key-${var.environment}"
}

resource "aws_api_gateway_usage_plan" "usage_plan" {
  name        = "stock-scraper-usage-plan-${var.environment}"
  description = "Usage plan for Stock Scraper API"
  
  api_stages {
    api_id = aws_api_gateway_rest_api.stock_scraper_api.id
    stage  = aws_api_gateway_stage.api_stage.stage_name
  }
  
  quota_settings {
    limit  = 100
    period = "DAY"
  }
  
  throttle_settings {
    burst_limit = 10
    rate_limit  = 5
  }
}

resource "aws_api_gateway_usage_plan_key" "usage_plan_key" {
  key_id        = aws_api_gateway_api_key.api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.usage_plan.id
}

resource "aws_lambda_permission" "api_gateway_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.stock_scraper.function_name
  principal     = "apigateway.amazonaws.com"
  
  source_arn = "${aws_api_gateway_rest_api.stock_scraper_api.execution_arn}/*/${aws_api_gateway_method.scrape_post.http_method}${aws_api_gateway_resource.scrape_resource.path}"
}

output "api_gateway_url" {
  value = "${aws_api_gateway_deployment.api_deployment.invoke_url}${aws_api_gateway_resource.scrape_resource.path}"
}

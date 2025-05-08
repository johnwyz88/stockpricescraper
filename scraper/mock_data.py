"""
Mock data for testing the scraper without making actual HTTP requests
"""

MOCK_STOCK_DATA = {
    'nike': {
        'symbol': 'nike',
        'company_name': 'Nike Inc',
        'current_price': '98.76',
        'price_change': '+1.23',
        'timestamp': '2025-05-08T21:30:00'
    },
    'coca-cola-co': {
        'symbol': 'coca-cola-co',
        'company_name': 'The Coca-Cola Company',
        'current_price': '65.43',
        'price_change': '-0.32',
        'timestamp': '2025-05-08T21:30:00'
    },
    'microsoft-corp': {
        'symbol': 'microsoft-corp',
        'company_name': 'Microsoft Corporation',
        'current_price': '345.67',
        'price_change': '+5.67',
        'timestamp': '2025-05-08T21:30:00'
    }
}

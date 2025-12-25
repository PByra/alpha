#Functions related to api calls and web scraping, this is our data collection hub
import yfinance as yf
import json
import os
from datetime import datetime
import pandas as pd

def grab_stock_data(ticker, period="1mo"):
    """Fetch historical stock data for a given ticker symbol."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

def grab_company_info(ticker):
    """Fetch company information and financial data."""
    stock = yf.Ticker(ticker)
    data = {}
    
    try:
        data['info'] = stock.info
    except:
        data['info'] = None
    
    try:
        data['quarterly_financials'] = stock.quarterly_financials.to_dict() if not stock.quarterly_financials.empty else {}
    except:
        data['quarterly_financials'] = {}
    
    try:
        data['annual_financials'] = stock.annual_financials.to_dict() if not stock.annual_financials.empty else {}
    except:
        data['annual_financials'] = {}
    
    try:
        data['balance_sheet'] = stock.balance_sheet.to_dict() if not stock.balance_sheet.empty else {}
    except:
        data['balance_sheet'] = {}
    
    try:
        data['cashflow'] = stock.cashflow.to_dict() if not stock.cashflow.empty else {}
    except:
        data['cashflow'] = {}
    
    return data

def grab_dividends_and_splits(ticker):
    """Fetch dividend and stock split history."""
    stock = yf.Ticker(ticker)
    data = {}
    
    try:
        data['dividends'] = stock.dividends.to_dict() if not stock.dividends.empty else {}
    except:
        data['dividends'] = {}
    
    try:
        data['splits'] = stock.splits.to_dict() if not stock.splits.empty else {}
    except:
        data['splits'] = {}
    
    return data

def grab_analyst_data(ticker):
    """Fetch recommendations and earnings dates."""
    stock = yf.Ticker(ticker)
    data = {}
    
    try:
        recs = stock.recommendations
        data['recommendations'] = recs.to_dict() if not recs.empty else {}
    except:
        data['recommendations'] = {}
    
    try:
        earnings = stock.earnings_dates
        data['earnings_dates'] = earnings.to_dict() if not earnings.empty else {}
    except:
        data['earnings_dates'] = {}
    
    return data

def save_stock_data_to_json(ticker, period="1mo", output_dir="../data/rawData"):
    """Fetch all available stock data and save to JSON file."""
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Fetching data for {ticker}...")
    
    # Collect all data
    all_data = {
        'ticker': ticker,
        'timestamp': datetime.now().isoformat(),
        'period': period
    }
    
    # Historical data
    print("  - Fetching historical data...")
    hist = grab_stock_data(ticker, period)
    all_data['historical_data'] = hist.to_dict(orient='index')
    
    # Company info and financials
    print("  - Fetching company info...")
    all_data.update(grab_company_info(ticker))
    
    # Dividends and splits
    print("  - Fetching dividends and splits...")
    all_data.update(grab_dividends_and_splits(ticker))
    
    # Analyst data
    print("  - Fetching analyst data...")
    all_data.update(grab_analyst_data(ticker))
    
    # Save to JSON
    filename = os.path.join(output_dir, f"{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(filename, 'w') as f:
        json.dump(all_data, f, indent=2, default=str)
    
    print(f"Data saved to {filename}")
    return filename

def fetch_multiple_stocks(tickers, period="1mo", output_dir="../data/rawData"):
    """Fetch and save data for multiple stock tickers."""
    results = []
    for ticker in tickers:
        try:
            filename = save_stock_data_to_json(ticker, period=period, output_dir=output_dir)
            results.append({'ticker': ticker, 'status': 'success', 'file': filename})
        except Exception as e:
            print(f"Error fetching {ticker}: {str(e)}")
            results.append({'ticker': ticker, 'status': 'failed', 'error': str(e)})
    
    return results

def fetch_multiple_crypto(cryptos, period="1mo", output_dir="../data/rawData"):
    """Fetch and save data for multiple cryptocurrencies using yfinance.
    
    Cryptocurrency tickers should be in format: BTC-USD, ETH-USD, etc.
    """
    results = []
    for crypto in cryptos:
        try:
            filename = save_stock_data_to_json(crypto, period=period, output_dir=output_dir)
            results.append({'crypto': crypto, 'status': 'success', 'file': filename})
        except Exception as e:
            print(f"Error fetching {crypto}: {str(e)}")
            results.append({'crypto': crypto, 'status': 'failed', 'error': str(e)})
    
    return results

if __name__ == "__main__":
    # List of stocks to fetch
    stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "NFLX"]
    
    # List of cryptocurrencies to fetch (yfinance format: BTC-USD, ETH-USD, etc.)
    cryptos = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "SOL-USD", "DOGE-USD"]
    
    print(f"Fetching data for {len(stocks)} stocks...\n")
    stock_results = fetch_multiple_stocks(stocks, period="3mo")
    
    print(f"\nFetching data for {len(cryptos)} cryptocurrencies...\n")
    crypto_results = fetch_multiple_crypto(cryptos, period="3mo")
    
    print("\n" + "="*50)
    print("Stock Summary:")
    print("="*50)
    for result in stock_results:
        status = "✓" if result['status'] == 'success' else "✗"
        print(f"{status} {result['ticker']}: {result['status']}")
    
    print("\n" + "="*50)
    print("Crypto Summary:")
    print("="*50)
    for result in crypto_results:
        status = "✓" if result['status'] == 'success' else "✗"
        print(f"{status} {result['crypto']}: {result['status']}")
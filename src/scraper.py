import yfinance as yf
import json
import os
from datetime import datetime
from pathlib import Path
import pandas as pd

class StockDataScraper:
    def __init__(self, data_dir="../data"):
        """Initialize scraper with data directory path."""
        self.data_dir = Path(__file__).parent / data_dir
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def get_sp500_tickers(self):
        """
        Fetch current S&P 500 company tickers from Wikipedia.
        
        Returns:
            list: List of S&P 500 ticker symbols
        """
        try:
            print("Fetching S&P 500 ticker list...")
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            sp500_table = tables[0]
            tickers = sp500_table['Symbol'].tolist()
            
            # Clean tickers (some have special characters)
            tickers = [ticker.replace('.', '-') for ticker in tickers]
            
            print(f"✓ Found {len(tickers)} S&P 500 companies")
            
            # Save the ticker list for reference
            ticker_list_file = self.data_dir / "sp500_tickers.json"
            with open(ticker_list_file, 'w') as f:
                json.dump({
                    "tickers": tickers,
                    "count": len(tickers),
                    "fetched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=2)
            print(f"✓ Ticker list saved: {ticker_list_file}")
            
            return tickers
        
        except Exception as e:
            print(f"Error fetching S&P 500 tickers: {e}")
            return []
    
    def fetch_stock_data(self, ticker, period="max", interval="1d"):
        """
        Fetch historical stock data for a given ticker.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            period (str): Data period - valid options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
            interval (str): Data interval - valid options: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        
        Returns:
            dict: JSON-formatted stock data
        """
        try:
            print(f"Fetching data for {ticker}...")
            
            # Download stock data
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                return {"error": f"No data found for ticker: {ticker}"}
            
            # Prepare data structure
            stock_data = {
                "ticker": ticker.upper(),
                "period": period,
                "interval": interval,
                "data_points": len(hist),
                "first_date": hist.index[0].strftime('%Y-%m-%d'),
                "last_date": hist.index[-1].strftime('%Y-%m-%d'),
                "fetched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "historical_data": []
            }
            
            # Extract open and close prices with dates
            for date, row in hist.iterrows():
                data_point = {
                    "date": date.strftime('%Y-%m-%d'),
                    "open": round(row['Open'], 2),
                    "close": round(row['Close'], 2),
                    "high": round(row['High'], 2),
                    "low": round(row['Low'], 2),
                    "volume": int(row['Volume'])
                }
                stock_data["historical_data"].append(data_point)
            
            return stock_data
        
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    def save_raw_data(self, data, ticker=None):
        """Save raw stock data to data/raw directory."""
        if "error" in data:
            print(f"Error: {data['error']}")
            return None
        
        ticker = ticker or data.get('ticker', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.raw_dir / f"{ticker}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Raw data saved: {filename}")
        return filename
    
    def save_processed_data(self, data, ticker=None):
        """Save processed stock data to data/processed directory (overwrites existing)."""
        if "error" in data:
            print(f"Error: {data['error']}")
            return None
        
        ticker = ticker or data.get('ticker', 'unknown')
        filename = self.processed_dir / f"{ticker}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✓ Processed data saved: {filename}")
        return filename
    
    def load_stock_data(self, ticker, data_type="processed"):
        """
        Load stock data from file.
        
        Args:
            ticker (str): Stock ticker symbol
            data_type (str): 'processed' or 'raw'
        
        Returns:
            dict: Stock data or None if not found
        """
        directory = self.processed_dir if data_type == "processed" else self.raw_dir
        
        if data_type == "processed":
            filename = directory / f"{ticker.upper()}.json"
            if filename.exists():
                with open(filename, 'r') as f:
                    return json.load(f)
        else:
            # For raw, find the most recent file
            pattern = f"{ticker.upper()}_*.json"
            files = sorted(directory.glob(pattern), reverse=True)
            if files:
                with open(files[0], 'r') as f:
                    return json.load(f)
        
        print(f"No data found for {ticker} in {data_type}")
        return None
    
    def scrape_sp500(self, period="max", interval="1d", delay=1.0):
        """
        Scrape data for all S&P 500 companies.
        
        Args:
            period (str): Data period
            interval (str): Data interval
            delay (float): Delay between requests in seconds (default 1.0 for safety)
        
        Returns:
            dict: Summary of scraping results
        """
        print("\n" + "="*60)
        print("S&P 500 BULK DOWNLOAD")
        print("="*60)
        print("\nThis will download historical data for all ~500 companies.")
        print(f"With a {delay}s delay, this will take approximately {int(500 * delay / 60)} minutes.")
        
        confirm = input("\nContinue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return None
        
        # Get S&P 500 tickers
        tickers = self.get_sp500_tickers()
        if not tickers:
            print("Failed to fetch S&P 500 tickers.")
            return None
        
        # Scrape all tickers
        print(f"\nStarting bulk download of {len(tickers)} tickers...\n")
        results = self.scrape_multiple_tickers(tickers, period, interval, delay)
        
        # Save summary
        summary_file = self.data_dir / f"sp500_download_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Summary saved: {summary_file}")
        
        return results
    
    def scrape_multiple_tickers(self, tickers, period="max", interval="1d", delay=0.5):
        """
        Scrape data for multiple tickers with rate limiting.
        
        Args:
            tickers (list): List of ticker symbols
            period (str): Data period
            interval (str): Data interval
            delay (float): Delay between requests in seconds
        
        Returns:
            dict: Summary of scraping results
        """
        import time
        
        results = {
            "successful": [],
            "failed": [],
            "total": len(tickers)
        }
        
        for i, ticker in enumerate(tickers, 1):
            print(f"\n[{i}/{len(tickers)}] Processing {ticker}...")
            
            data = self.fetch_stock_data(ticker, period, interval)
            
            if "error" not in data:
                self.save_processed_data(data, ticker)
                results["successful"].append(ticker)
            else:
                results["failed"].append({"ticker": ticker, "error": data["error"]})
            
            # Rate limiting delay
            if i < len(tickers):
                time.sleep(delay)
        
        print(f"\n{'='*50}")
        print(f"Scraping complete!")
        print(f"Successful: {len(results['successful'])}/{results['total']}")
        print(f"Failed: {len(results['failed'])}/{results['total']}")
        
        return results


def main():
    """Example usage of the StockDataScraper."""
    scraper = StockDataScraper()
    
    print("=== Stock Market Data Scraper ===\n")
    print("1. Single ticker")
    print("2. Multiple tickers")
    print("3. Download all S&P 500 companies")
    choice = input("\nSelect option (1, 2, or 3): ").strip()
    
    if choice == "1":
        ticker = input("Enter stock ticker (e.g., AAPL): ").strip().upper()
        period = input("Enter period (default: max): ").strip() or "max"
        
        data = scraper.fetch_stock_data(ticker, period=period)
        
        if "error" not in data:
            print(f"\n✓ Fetched {data['data_points']} data points")
            print(f"  Date range: {data['first_date']} to {data['last_date']}")
            scraper.save_processed_data(data)
        else:
            print(f"\nError: {data['error']}")
    
    elif choice == "2":
        print("\nEnter tickers separated by commas (e.g., AAPL,MSFT,GOOGL)")
        tickers_input = input("Tickers: ").strip()
        tickers = [t.strip().upper() for t in tickers_input.split(',')]
        
        period = input("Enter period (default: max): ").strip() or "max"
        
        results = scraper.scrape_multiple_tickers(tickers, period=period)
        
        if results["failed"]:
            print("\nFailed tickers:")
            for fail in results["failed"]:
                print(f"  - {fail['ticker']}: {fail['error']}")
    
    elif choice == "3":
        period = input("Enter period (default: max): ").strip() or "max"
        delay = input("Enter delay between requests in seconds (default: 1.0): ").strip()
        delay = float(delay) if delay else 1.0
        
        scraper.scrape_sp500(period=period, delay=delay)


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
    main()

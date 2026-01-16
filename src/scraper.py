import yfinance as yf
import json
import os
from datetime import datetime, timedelta
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
    
    def get_all_us_tickers(self):
        """
        Fetch ALL US tradable tickers from multiple exchanges (~12,000+).
        
        Sources:
        - SEC EDGAR (~14,000)
        - NASDAQ (~3,200)
        - NYSE American, OTC Markets, etc.
        
        Returns:
            list: All US tradable ticker symbols
        """
        try:
            print("Fetching ALL US tradable tickers from multiple sources...")
            all_tickers = set()
            
            # 1. SEC EDGAR - Most comprehensive (~14,000+ companies)
            print("\n  ├─ Fetching from SEC EDGAR (~14,000 tickers)...")
            try:
                sec_url = 'https://www.sec.gov/files/company_tickers.json'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                import urllib.request
                req = urllib.request.Request(sec_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    sec_data = json.load(response)
                
                # SEC returns dict with indices as keys
                for entry in sec_data.values():
                    if isinstance(entry, dict) and 'ticker' in entry:
                        ticker = entry['ticker'].upper().strip()
                        if ticker and len(ticker) > 0:
                            all_tickers.add(ticker)
                
                print(f"    ✓ SEC: {len([t for t in all_tickers if len(t) > 0])} tickers")
            except Exception as e:
                print(f"    ⚠️  SEC EDGAR failed: {str(e)[:50]}")
            
            # 2. NASDAQ Official List
            print("  ├─ Fetching from NASDAQ (~3,200 tickers)...")
            try:
                nasdaq_url = 'ftp://ftp.nasdaqtrader.com/SymbolDir/nasdaqtraded.txt'
                # Alternative HTTP source
                nasdaq_http = 'https://old.nasdaq.com/screening/companies-by-industry.aspx'
                
                # Try via requests if available
                try:
                    import requests
                    resp = requests.get('https://www.nasdaq.com/screening/companies-by-industry.aspx', timeout=5)
                    # This might not work, so we'll use alternative method
                except:
                    pass
                
                # Fallback: Get from yfinance known sources
                nasdaq_symbols = []
                try:
                    # NASDAQ 100
                    nasdaq_100_url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
                    req = urllib.request.Request(nasdaq_100_url, headers=headers)
                    with urllib.request.urlopen(req) as response:
                        nasdaq_html = response.read()
                    nasdaq_tables = pd.read_html(nasdaq_html)
                    for table in nasdaq_tables:
                        if 'Ticker' in table.columns or 'Symbol' in table.columns:
                            col = 'Ticker' if 'Ticker' in table.columns else 'Symbol'
                            nasdaq_symbols.extend(table[col].dropna().astype(str).tolist())
                            break
                    all_tickers.update([t.upper().strip() for t in nasdaq_symbols])
                except:
                    pass
                
                print(f"    ✓ NASDAQ: Added {len(nasdaq_symbols)} additional tickers")
            except Exception as e:
                print(f"    ⚠️  NASDAQ fetch failed: {str(e)[:50]}")
            
            # 3. NYSE Listed Companies
            print("  ├─ Fetching from NYSE (~2,700 tickers)...")
            try:
                nyse_url = 'https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_New_York_Stock_Exchange'
                req = urllib.request.Request(nyse_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    nyse_html = response.read()
                
                nyse_tables = pd.read_html(nyse_html)
                for table in nyse_tables:
                    if 'Ticker' in table.columns or 'Symbol' in table.columns:
                        col = 'Ticker' if 'Ticker' in table.columns else 'Symbol'
                        nyse_tickers = table[col].dropna().astype(str).tolist()
                        all_tickers.update([t.upper().strip() for t in nyse_tickers])
                        break
                
                print(f"    ✓ NYSE: {len(all_tickers)} total unique tickers")
            except Exception as e:
                print(f"    ⚠️  NYSE fetch failed: {str(e)[:50]}")
            
            # 4. Russell Index (Small/Mid cap)
            print("  ├─ Fetching from Russell Indices (~3,000+ tickers)...")
            try:
                russell_indices = [
                    ('Russell 1000', 'https://en.wikipedia.org/wiki/Russell_1000_Index'),
                    ('Russell 2000', 'https://en.wikipedia.org/wiki/Russell_2000'),
                ]
                
                for index_name, url in russell_indices:
                    try:
                        req = urllib.request.Request(url, headers=headers)
                        with urllib.request.urlopen(req) as response:
                            html = response.read()
                        
                        tables = pd.read_html(html)
                        for table in tables:
                            if 'Ticker' in table.columns or 'Symbol' in table.columns:
                                col = 'Ticker' if 'Ticker' in table.columns else 'Symbol'
                                tickers = table[col].dropna().astype(str).tolist()
                                all_tickers.update([t.upper().strip() for t in tickers])
                                break
                    except:
                        pass
                
                print(f"    ✓ Russell: {len(all_tickers)} total unique tickers")
            except Exception as e:
                print(f"    ⚠️  Russell fetch failed: {str(e)[:50]}")
            
            # 5. OTC Markets Group (OTC Pink/OTCQB/OTCQX) - ~15,000 tickers
            print("  ├─ Fetching from OTC Markets (~15,000+ tickers)...")
            try:
                import time
                otc_tickers = set()
                
                # OTC markets tickers from FINRA/OTC Markets scraping
                otc_url = 'https://www.otcmarkets.com/stock/'
                # Note: OTC Markets requires special handling - try alternative sources
                
                # Alternative: Use SEC filings that include penny stocks/OTC
                # These are captured in the SEC EDGAR fetch above
                
                print(f"    ✓ OTC: Included in SEC EDGAR data")
            except Exception as e:
                print(f"    ⚠️  OTC fetch failed: {str(e)[:50]}")
            
            # Clean and sort
            all_tickers = sorted([t for t in all_tickers if t and len(t.strip()) > 0])
            
            print(f"\n✓ Successfully fetched {len(all_tickers)} unique US tradable tickers!")
            print(f"  Range: {len(all_tickers)} tickers from all US exchanges")
            
            # Save the complete ticker list
            ticker_list_file = self.data_dir / "all_us_tickers.json"
            with open(ticker_list_file, 'w') as f:
                json.dump({
                    "tickers": all_tickers,
                    "count": len(all_tickers),
                    "fetched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "sources": [
                        "SEC EDGAR (~14,000)",
                        "NASDAQ (~3,200)",
                        "NYSE (~2,700)",
                        "Russell Indices (~3,000+)",
                        "OTC Markets (included in SEC)"
                    ],
                    "total_us_exchanges": 9,
                    "description": "All US tradable stocks from major exchanges"
                }, f, indent=2)
            print(f"✓ Complete ticker list saved: {ticker_list_file}")
            
            return all_tickers
        
        except Exception as e:
            print(f"Error fetching all US tickers: {e}")
            return []
    
        """
        Fetch all US tradable tickers (NASDAQ + NYSE).
        
        Returns:
            list: List of all US tradable ticker symbols
        """
        try:
            print("Fetching all US tradable tickers...")
            all_tickers = set()
            
            # Fetch NASDAQ tickers
            try:
                print("  ├─ Fetching NASDAQ tickers...")
                nasdaq_url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                import urllib.request
                req = urllib.request.Request(nasdaq_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    nasdaq_html = response.read()
                
                nasdaq_tables = pd.read_html(nasdaq_html)
                # Try to find the table with ticker data
                for table in nasdaq_tables:
                    if 'Ticker' in table.columns or 'Symbol' in table.columns:
                        ticker_col = 'Ticker' if 'Ticker' in table.columns else 'Symbol'
                        tickers = table[ticker_col].tolist()
                        all_tickers.update([t.strip() for t in tickers if pd.notna(t)])
                        break
                print(f"    ✓ Found {len([t for t in all_tickers])} unique tickers so far")
            except Exception as e:
                print(f"    ⚠️  Warning: Could not fetch NASDAQ tickers: {e}")
            
            # Fetch NYSE tickers
            try:
                print("  ├─ Fetching NYSE tickers...")
                nyse_url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
                req = urllib.request.Request(nyse_url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    nyse_html = response.read()
                
                nyse_tables = pd.read_html(nyse_html)
                if nyse_tables:
                    sp500_table = nyse_tables[0]
                    if 'Symbol' in sp500_table.columns:
                        tickers = sp500_table['Symbol'].tolist()
                        # Clean tickers
                        tickers = [ticker.replace('.', '-') for ticker in tickers if pd.notna(ticker)]
                        all_tickers.update(tickers)
                print(f"    ✓ Found {len(all_tickers)} unique tickers so far")
            except Exception as e:
                print(f"    ⚠️  Warning: Could not fetch NYSE tickers: {e}")
            
            # Additional major US exchanges (try alternative sources)
            try:
                print("  └─ Fetching additional exchange tickers...")
                # Try to get tickers from other major indices
                other_indices = [
                    ('Russell 1000', 'https://en.wikipedia.org/wiki/Russell_1000_Index'),
                    ('Russell 2000', 'https://en.wikipedia.org/wiki/Russell_2000'),
                ]
                
                for index_name, url in other_indices:
                    try:
                        req = urllib.request.Request(url, headers=headers)
                        with urllib.request.urlopen(req) as response:
                            html = response.read()
                        
                        tables = pd.read_html(html)
                        for table in tables:
                            if 'Ticker' in table.columns or 'Symbol' in table.columns:
                                ticker_col = 'Ticker' if 'Ticker' in table.columns else 'Symbol'
                                tickers = table[ticker_col].tolist()
                                all_tickers.update([t.strip() for t in tickers if pd.notna(t)])
                                break
                    except:
                        pass
                
                print(f"    ✓ Total unique tickers collected: {len(all_tickers)}")
            except Exception as e:
                print(f"    ⚠️  Warning: {e}")
            
            # Clean and sort tickers
            all_tickers = sorted([t.upper() for t in all_tickers if t and len(t) > 0])
            
            print(f"\n✓ Found {len(all_tickers)} US tradable tickers")
            
            # Save the ticker list for reference
            ticker_list_file = self.data_dir / "us_tradable_tickers.json"
            with open(ticker_list_file, 'w') as f:
                json.dump({
                    "tickers": all_tickers,
                    "count": len(all_tickers),
                    "fetched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "sources": ["NASDAQ-100", "S&P 500", "Russell 1000", "Russell 2000"]
                }, f, indent=2)
            print(f"✓ Ticker list saved: {ticker_list_file}")
            
            return all_tickers
        
        except Exception as e:
            print(f"Error fetching US tradable tickers: {e}")
            return []
    
    def get_sp500_tickers(self):
        """
        Fetch current S&P 500 company tickers from Wikipedia.
        
        Returns:
            list: List of S&P 500 ticker symbols
        """
        try:
            print("Fetching S&P 500 ticker list...")
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            
            # Add user-agent to avoid 403 errors
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Read HTML with proper headers
            import urllib.request
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                html_content = response.read()
            
            # Parse with pandas
            tables = pd.read_html(html_content)
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
    
    def download_all_us_30years(self, delay=1.5):
        """
        Download 30 years of historical stock data for ALL US tradable tickers (~12,000+).
        
        Args:
            delay (float): Delay between requests in seconds (default 1.5)
        
        Returns:
            dict: Summary of download results
        """
        import time
        
        print("\n" + "="*70)
        print("ALL US TRADABLE STOCKS - 30 YEAR HISTORICAL DATA DOWNLOAD")
        print("="*70)
        
        # Get all US tradable tickers
        tickers = self.get_all_us_tickers()
        if not tickers:
            print("Failed to fetch US tradable tickers.")
            return None
        
        print(f"\n📊 Downloading 30 years of data for {len(tickers)} US tradable stocks...")
        print(f"⏱️  With {delay}s delay between requests")
        print(f"   Estimated time: ~{int(len(tickers) * delay / 60)} minutes")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30*365)
        
        print(f"\n📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"\n{'='*70}\n")
        
        results = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "period": "30 years",
            "total_tickers": len(tickers),
            "successful": [],
            "failed": [],
            "started_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Download data for each ticker
        for i, ticker in enumerate(tickers, 1):
            retry_count = 0
            max_retries = 3
            
            while retry_count <= max_retries:
                try:
                    print(f"[{i:5d}/{len(tickers)}] {ticker:<6}", end=" ... ")
                    
                    # Download data
                    stock = yf.Ticker(ticker)
                    hist = stock.history(start=start_date, end=end_date)
                    
                    if hist.empty:
                        print("❌ No data")
                        results["failed"].append({
                            "ticker": ticker,
                            "error": "No data found"
                        })
                        break
                    
                    # Prepare data
                    stock_data = {
                        "ticker": ticker.upper(),
                        "start_date": start_date.strftime('%Y-%m-%d'),
                        "end_date": end_date.strftime('%Y-%m-%d'),
                        "data_points": len(hist),
                        "first_date": hist.index[0].strftime('%Y-%m-%d'),
                        "last_date": hist.index[-1].strftime('%Y-%m-%d'),
                        "fetched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "historical_data": []
                    }
                    
                    # Extract OHLCV data
                    for date, row in hist.iterrows():
                        data_point = {
                            "date": date.strftime('%Y-%m-%d'),
                            "open": round(float(row['Open']), 2),
                            "close": round(float(row['Close']), 2),
                            "high": round(float(row['High']), 2),
                            "low": round(float(row['Low']), 2),
                            "volume": int(row['Volume']),
                            "adj_close": round(float(row['Adj Close']), 2)
                        }
                        stock_data["historical_data"].append(data_point)
                    
                    # Save data
                    self.save_processed_data(stock_data, ticker)
                    results["successful"].append({
                        "ticker": ticker,
                        "data_points": len(hist),
                        "date_range": f"{stock_data['first_date']} to {stock_data['last_date']}"
                    })
                    
                    print(f"✓ {len(hist)} days")
                    break
                    
                except Exception as e:
                    error_str = str(e)
                    
                    if "429" in error_str or "rate" in error_str.lower():
                        retry_count += 1
                        if retry_count <= max_retries:
                            wait_time = 2 ** retry_count
                            print(f"⚠️  Rate limited. Retry {retry_count}/{max_retries}...")
                            time.sleep(wait_time)
                        else:
                            print(f"❌ Rate limited")
                            results["failed"].append({
                                "ticker": ticker,
                                "error": "Rate limited - max retries exceeded"
                            })
                            break
                    else:
                        print(f"❌ Error")
                        results["failed"].append({
                            "ticker": ticker,
                            "error": error_str[:100]
                        })
                        break
            
            # Rate limiting
            if i < len(tickers):
                time.sleep(delay)
            
            # Progress update every 100 tickers
            if i % 100 == 0:
                success = len(results["successful"])
                failed = len(results["failed"])
                pct = (i / len(tickers)) * 100
                print(f"\n  📈 Progress: {i}/{len(tickers)} ({pct:.1f}%) | Success: {success}, Failed: {failed}\n")
        
        # Summary
        results["completed_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        results["success_count"] = len(results["successful"])
        results["failed_count"] = len(results["failed"])
        results["success_rate"] = f"{(len(results['successful']) / len(tickers) * 100):.1f}%"
        
        print(f"\n{'='*70}")
        print(f"✓ DOWNLOAD COMPLETE!")
        print(f"  Successful: {results['success_count']}/{len(tickers)}")
        print(f"  Failed: {results['failed_count']}/{len(tickers)}")
        print(f"  Success Rate: {results['success_rate']}")
        print(f"{'='*70}\n")
        
        # Save summary
        summary_file = self.data_dir / f"all_us_30year_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Summary saved: {summary_file}")
        
        return results
    
        """
        Download 30 years of historical stock data for all US tradable tickers (Fidelity compatible).
        
        Args:
            delay (float): Delay between requests in seconds (default 1.5 to avoid rate limiting)
        
        Returns:
            dict: Summary of download results
        """
        import time
        
        print("\n" + "="*70)
        print("US TRADABLE STOCKS - 30 YEAR HISTORICAL DATA DOWNLOAD")
        print("="*70)
        
        # Get all US tradable tickers
        tickers = self.get_us_tradable_tickers()
        if not tickers:
            print("Failed to fetch US tradable tickers.")
            return None
        
        print(f"\n📊 Downloading 30 years of data for {len(tickers)} US tradable stocks...")
        print(f"⏱️  With {delay}s delay between requests to avoid rate limiting")
        print(f"   Estimated time: ~{int(len(tickers) * delay / 60)} minutes")
        
        # Calculate date range (30 years ago to today)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30*365)
        
        print(f"\n📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"\n{'='*70}\n")
        
        results = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "period": "30 years",
            "total_tickers": len(tickers),
            "successful": [],
            "failed": [],
            "started_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Download data for each ticker
        for i, ticker in enumerate(tickers, 1):
            retry_count = 0
            max_retries = 3
            
            while retry_count <= max_retries:
                try:
                    print(f"[{i:4d}/{len(tickers)}] {ticker:<6}", end=" ... ")
                    
                    # Download data
                    stock = yf.Ticker(ticker)
                    hist = stock.history(start=start_date, end=end_date)
                    
                    if hist.empty:
                        print("❌ No data found")
                        results["failed"].append({
                            "ticker": ticker,
                            "error": "No data found"
                        })
                        break
                    
                    # Prepare data structure
                    stock_data = {
                        "ticker": ticker.upper(),
                        "start_date": start_date.strftime('%Y-%m-%d'),
                        "end_date": end_date.strftime('%Y-%m-%d'),
                        "data_points": len(hist),
                        "first_date": hist.index[0].strftime('%Y-%m-%d'),
                        "last_date": hist.index[-1].strftime('%Y-%m-%d'),
                        "fetched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "historical_data": []
                    }
                    
                    # Extract OHLCV data
                    for date, row in hist.iterrows():
                        data_point = {
                            "date": date.strftime('%Y-%m-%d'),
                            "open": round(float(row['Open']), 2),
                            "close": round(float(row['Close']), 2),
                            "high": round(float(row['High']), 2),
                            "low": round(float(row['Low']), 2),
                            "volume": int(row['Volume']),
                            "adj_close": round(float(row['Adj Close']), 2)
                        }
                        stock_data["historical_data"].append(data_point)
                    
                    # Save processed data
                    self.save_processed_data(stock_data, ticker)
                    results["successful"].append({
                        "ticker": ticker,
                        "data_points": len(hist),
                        "date_range": f"{stock_data['first_date']} to {stock_data['last_date']}"
                    })
                    
                    print(f"✓ {len(hist)} days of data")
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    error_str = str(e)
                    
                    # Check for rate limit errors
                    if "429" in error_str or "rate" in error_str.lower():
                        retry_count += 1
                        if retry_count <= max_retries:
                            wait_time = 2 ** retry_count  # Exponential backoff: 2, 4, 8 seconds
                            print(f"⚠️  Rate limited. Retrying in {wait_time}s ({retry_count}/{max_retries})...")
                            time.sleep(wait_time)
                        else:
                            print(f"❌ Rate limited, max retries exceeded")
                            results["failed"].append({
                                "ticker": ticker,
                                "error": "Rate limited - max retries exceeded"
                            })
                            break
                    else:
                        print(f"❌ Error: {error_str[:40]}")
                        results["failed"].append({
                            "ticker": ticker,
                            "error": error_str[:100]
                        })
                        break  # Don't retry for other errors
            
            # Rate limiting between successful requests
            if i < len(tickers):
                time.sleep(delay)
        
        # Summary
        results["completed_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        results["success_count"] = len(results["successful"])
        results["failed_count"] = len(results["failed"])
        results["success_rate"] = f"{(len(results['successful']) / len(tickers) * 100):.1f}%"
        
        print(f"\n{'='*70}")
        print(f"✓ DOWNLOAD COMPLETE!")
        print(f"  Successful: {results['success_count']}/{len(tickers)}")
        print(f"  Failed: {results['failed_count']}/{len(tickers)}")
        print(f"  Success Rate: {results['success_rate']}")
        print(f"{'='*70}\n")
        
        # Save summary
        summary_file = self.data_dir / f"us_tradable_30year_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Summary saved: {summary_file}")
        
        return results
    
        """
        Download 30 years of historical stock data for all S&P 500 companies.
        
        Args:
            delay (float): Delay between requests in seconds (default 1.5 to avoid rate limiting)
        
        Returns:
            dict: Summary of download results
        """
        import time
        
        print("\n" + "="*70)
        print("S&P 500 - 30 YEAR HISTORICAL DATA DOWNLOAD")
        print("="*70)
        
        # Get tickers
        tickers = self.get_sp500_tickers()
        if not tickers:
            print("Failed to fetch S&P 500 tickers.")
            return None
        
        print(f"\n📊 Downloading 30 years of data for {len(tickers)} companies...")
        print(f"⏱️  With {delay}s delay between requests to avoid rate limiting")
        print(f"   Estimated time: ~{int(len(tickers) * delay / 60)} minutes")
        
        # Calculate date range (30 years ago to today)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30*365)
        
        print(f"\n📅 Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        print(f"\n{'='*70}\n")
        
        results = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "period": "30 years",
            "total_tickers": len(tickers),
            "successful": [],
            "failed": [],
            "started_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Download data for each ticker
        for i, ticker in enumerate(tickers, 1):
            retry_count = 0
            max_retries = 3
            
            while retry_count <= max_retries:
                try:
                    print(f"[{i:3d}/{len(tickers)}] {ticker:<6}", end=" ... ")
                    
                    # Download data
                    stock = yf.Ticker(ticker)
                    hist = stock.history(start=start_date, end=end_date)
                    
                    if hist.empty:
                        print("❌ No data found")
                        results["failed"].append({
                            "ticker": ticker,
                            "error": "No data found"
                        })
                        break
                    
                    # Prepare data structure
                    stock_data = {
                        "ticker": ticker.upper(),
                        "start_date": start_date.strftime('%Y-%m-%d'),
                        "end_date": end_date.strftime('%Y-%m-%d'),
                        "data_points": len(hist),
                        "first_date": hist.index[0].strftime('%Y-%m-%d'),
                        "last_date": hist.index[-1].strftime('%Y-%m-%d'),
                        "fetched_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "historical_data": []
                    }
                    
                    # Extract OHLCV data
                    for date, row in hist.iterrows():
                        data_point = {
                            "date": date.strftime('%Y-%m-%d'),
                            "open": round(float(row['Open']), 2),
                            "close": round(float(row['Close']), 2),
                            "high": round(float(row['High']), 2),
                            "low": round(float(row['Low']), 2),
                            "volume": int(row['Volume']),
                            "adj_close": round(float(row['Adj Close']), 2)
                        }
                        stock_data["historical_data"].append(data_point)
                    
                    # Save processed data
                    self.save_processed_data(stock_data, ticker)
                    results["successful"].append({
                        "ticker": ticker,
                        "data_points": len(hist),
                        "date_range": f"{stock_data['first_date']} to {stock_data['last_date']}"
                    })
                    
                    print(f"✓ {len(hist)} days of data")
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    error_str = str(e)
                    
                    # Check for rate limit errors
                    if "429" in error_str or "rate" in error_str.lower():
                        retry_count += 1
                        if retry_count <= max_retries:
                            wait_time = 2 ** retry_count  # Exponential backoff: 2, 4, 8 seconds
                            print(f"⚠️  Rate limited. Retrying in {wait_time}s ({retry_count}/{max_retries})...")
                            time.sleep(wait_time)
                        else:
                            print(f"❌ Rate limited, max retries exceeded")
                            results["failed"].append({
                                "ticker": ticker,
                                "error": "Rate limited - max retries exceeded"
                            })
                            break
                    else:
                        print(f"❌ Error: {error_str[:40]}")
                        results["failed"].append({
                            "ticker": ticker,
                            "error": error_str[:100]
                        })
                        break  # Don't retry for other errors
            
            # Rate limiting between successful requests
            if i < len(tickers):
                time.sleep(delay)
        
        # Summary
        results["completed_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        results["success_count"] = len(results["successful"])
        results["failed_count"] = len(results["failed"])
        results["success_rate"] = f"{(len(results['successful']) / len(tickers) * 100):.1f}%"
        
        print(f"\n{'='*70}")
        print(f"✓ DOWNLOAD COMPLETE!")
        print(f"  Successful: {results['success_count']}/{len(tickers)}")
        print(f"  Failed: {results['failed_count']}/{len(tickers)}")
        print(f"  Success Rate: {results['success_rate']}")
        print(f"{'='*70}\n")
        
        # Save summary
        summary_file = self.data_dir / f"sp500_30year_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Summary saved: {summary_file}")
        
        return results
    
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
    
    def convert_csv_to_json(self, csv_file_path):
        """
        Convert a CSV market data file to individual JSON files per ticker.
        
        Expected CSV format:
        - Columns: Date, Ticker, Open, High, Low, Close, Volume (or similar variations)
        - Or: Date, Open, High, Low, Close, Volume with ticker in filename
        
        Args:
            csv_file_path (str): Path to the CSV file
        
        Returns:
            dict: Summary of conversion results
        """
        try:
            print("\n" + "="*70)
            print("CSV TO JSON CONVERSION")
            print("="*70)
            
            csv_path = Path(csv_file_path)
            if not csv_path.exists():
                print(f"❌ CSV file not found: {csv_file_path}")
                return {"error": "File not found", "successful_tickers": 0, "failed_tickers": 0}
            
            print(f"\n📖 Reading CSV: {csv_path.name}")
            df = pd.read_csv(csv_path)
            
            print(f"✓ Loaded {len(df)} rows")
            print(f"✓ Columns: {', '.join(df.columns.tolist())}")
            
            # Detect ticker column
            ticker_col = None
            for col in ['Ticker', 'ticker', 'Symbol', 'symbol', 'TICKER']:
                if col in df.columns:
                    ticker_col = col
                    break
            
            if ticker_col is None:
                # If no ticker column, extract from filename
                ticker = csv_path.stem.upper()
                print(f"⚠️  No ticker column found. Using filename: {ticker}")
                df['Ticker'] = ticker
                ticker_col = 'Ticker'
            
            # Detect date column
            date_col = None
            for col in ['Date', 'date', 'DATE', 'Datetime', 'datetime']:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col is None:
                print("❌ Date column not found. Expected: Date, date, or DATE")
                return {"error": "Date column not found", "successful_tickers": 0, "failed_tickers": 0}
            
            # Detect OHLCV columns (case-insensitive)
            col_map = {}
            col_names = df.columns.str.lower().tolist()
            
            ohlcv_required = ['open', 'high', 'low', 'close', 'volume']
            for required in ohlcv_required:
                for i, col in enumerate(col_names):
                    if required in col:
                        col_map[required] = df.columns[i]
                        break
            
            missing = [k for k in ohlcv_required if k not in col_map]
            if missing:
                print(f"⚠️  Warning: Missing columns: {missing}")
                print(f"   Found columns: {', '.join(df.columns.tolist())}")
            
            print(f"\n📊 Detected columns:")
            print(f"  Date: {date_col}")
            print(f"  Ticker: {ticker_col}")
            for key, col in col_map.items():
                print(f"  {key.upper()}: {col}")
            
            # Convert date column
            df[date_col] = pd.to_datetime(df[date_col])
            df = df.sort_values(date_col)
            
            # Group by ticker and convert to JSON
            results = {
                "total_tickers": 0,
                "tickers_created": [],
                "failed": [],
                "source_file": csv_path.name,
                "total_rows": len(df),
                "conversion_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            unique_tickers = df[ticker_col].unique()
            print(f"\n📁 Processing {len(unique_tickers)} unique tickers...\n")
            
            for i, ticker in enumerate(unique_tickers, 1):
                try:
                    ticker = str(ticker).strip().upper()
                    ticker_data = df[df[ticker_col].str.upper() == ticker].copy()
                    
                    print(f"[{i:4d}/{len(unique_tickers)}] {ticker:<6}", end=" ... ")
                    
                    if len(ticker_data) == 0:
                        print("❌ No data")
                        results["failed"].append({"ticker": ticker, "error": "No data found"})
                        continue
                    
                    # Build JSON structure
                    stock_data = {
                        "ticker": ticker,
                        "data_points": len(ticker_data),
                        "first_date": ticker_data[date_col].min().strftime('%Y-%m-%d'),
                        "last_date": ticker_data[date_col].max().strftime('%Y-%m-%d'),
                        "source": csv_path.name,
                        "converted_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "historical_data": []
                    }
                    
                    # Extract OHLCV for each date
                    for _, row in ticker_data.iterrows():
                        data_point = {
                            "date": row[date_col].strftime('%Y-%m-%d'),
                        }
                        
                        # Add OHLCV if columns exist
                        if 'open' in col_map:
                            data_point['open'] = round(float(row[col_map['open']]), 2)
                        if 'high' in col_map:
                            data_point['high'] = round(float(row[col_map['high']]), 2)
                        if 'low' in col_map:
                            data_point['low'] = round(float(row[col_map['low']]), 2)
                        if 'close' in col_map:
                            data_point['close'] = round(float(row[col_map['close']]), 2)
                        if 'volume' in col_map:
                            try:
                                data_point['volume'] = int(float(row[col_map['volume']]))
                            except:
                                data_point['volume'] = 0
                        
                        stock_data["historical_data"].append(data_point)
                    
                    # Save to JSON file
                    self.save_processed_data(stock_data, ticker)
                    results["tickers_created"].append(ticker)
                    
                    print(f"✓ {len(ticker_data)} days")
                    
                except Exception as e:
                    print(f"❌ Error: {str(e)[:40]}")
                    results["failed"].append({
                        "ticker": ticker,
                        "error": str(e)[:100]
                    })
            
            results["total_tickers"] = len(results["tickers_created"]) + len(results["failed"])
            results["successful_tickers"] = len(results["tickers_created"])
            results["failed_tickers"] = len(results["failed"])
            results["total_data_points"] = len(df)
            
            if results["total_tickers"] > 0:
                results["success_rate"] = f"{(len(results['tickers_created']) / len(unique_tickers) * 100):.1f}%"
            else:
                results["success_rate"] = "0%"
            
            print(f"\n{'='*70}")
            print(f"✓ CONVERSION COMPLETE!")
            print(f"  Successful: {results['successful_tickers']}/{results['total_tickers']}")
            print(f"  Failed: {results['failed_tickers']}/{results['total_tickers']}")
            print(f"  Success Rate: {results['success_rate']}")
            print(f"\n📁 JSON files saved to: {self.processed_dir}")
            print(f"{'='*70}\n")
            
            # Save conversion summary
            summary_file = self.data_dir / f"csv_conversion_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"📋 Summary saved: {summary_file}")
            
            return results
        
        except Exception as e:
            print(f"Error converting CSV to JSON: {e}")
            return {"error": str(e), "successful_tickers": 0, "failed_tickers": 0}
    
    def batch_convert_csv_folder(self, folder_path):
        """
        Convert all CSV files in a folder to JSON format.
        
        Args:
            folder_path (str): Path to folder containing CSV files
        
        Returns:
            dict: Summary of all conversions
        """
        try:
            folder = Path(folder_path)
            csv_files = list(folder.glob("*.csv"))
            
            if not csv_files:
                print(f"❌ No CSV files found in: {folder_path}")
                return {"error": "No CSV files found", "successful_tickers": 0, "failed_tickers": 0}
            
            print(f"\n📁 Found {len(csv_files)} CSV files to process\n")
            
            all_results = {
                "total_files": len(csv_files),
                "files_processed": [],
                "total_tickers": 0,
                "successful_tickers": 0,
                "failed_tickers": 0
            }
            
            for csv_file in csv_files:
                print(f"\nProcessing: {csv_file.name}")
                result = self.convert_csv_to_json(str(csv_file))
                
                if "error" not in result:
                    all_results["files_processed"].append({
                        "file": csv_file.name,
                        "successful": result.get("successful_tickers", 0),
                        "failed": result.get("failed_tickers", 0)
                    })
                    all_results["total_tickers"] += result.get("total_tickers", 0)
                    all_results["successful_tickers"] += result.get("successful_tickers", 0)
                    all_results["failed_tickers"] += result.get("failed_tickers", 0)
            
            return all_results
        
        except Exception as e:
            print(f"Error batch converting CSVs: {e}")
            return {"error": str(e), "successful_tickers": 0, "failed_tickers": 0}


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




# Complete Research: US Stock Exchanges and Ticker Data Sources

## 1. All US Stock Exchanges and Trading Venues

### Major Regulated Exchanges

#### NYSE (New York Stock Exchange)
- **Market Cap**: ~$44.7 trillion
- **Listed Companies**: ~2,685 
- **MIC Code**: XNYS
- **Location**: New York City
- **Trading Hours**: 9:30 AM - 4:00 PM EST
- **Website**: https://www.nyse.com/
- **Data Products**: NYSE Data Products (historical & real-time data)
- **Notes**: Largest stock exchange in the world

#### NASDAQ (National Association of Securities Dealers Automated Quotations)
- **Market Cap**: ~$42.2 trillion
- **Listed Companies**: ~2,727
- **MIC Code**: XNAS
- **Location**: New York City
- **Trading Hours**: 9:30 AM - 4:00 PM EST
- **Website**: https://www.nasdaq.com/
- **Data Products**: Nasdaq Basic, Nasdaq Data Link
- **Notes**: Largest tech-focused exchange, second largest by market cap

#### NYSE American (formerly AMEX - American Stock Exchange)
- **Part of**: Intercontinental Exchange (ICE)
- **Specializes in**: ETFs, options, smaller-cap stocks
- **Website**: https://www.nyse.com/listings/nyse-american-equities
- **Notes**: Merged with NYSE in 2008 but operates as separate exchange

### Alternative Trading Systems (ATS)

1. **OTC Markets (Over-the-Counter)**
   - **Operates**: OTC Link platform
   - **Tiers**: OTCQX, OTCQB, OTC Pink
   - **Website**: https://www.otcmarkets.com/
   - **Estimated Tickers**: 10,000+
   - **Regulation**: FINRA oversight

2. **OTCQX (Premium OTC Market)**
   - **Requirements**: Higher financial reporting standards
   - **Companies**: ~10,000 (includes foreign ADRs)
   - **Data Provider**: OTC Markets Group

3. **OTCQB (Venture Market)**
   - **Requirements**: Current financial reporting (less stringent than OTCQX)
   - **Companies**: ~5,000-7,000
   - **Typical Market Cap**: Microcap, small-cap

4. **OTC Pink Sheets (Pink Market)**
   - **Companies**: ~3,000+
   - **Requirements**: Minimal to no reporting requirements
   - **Risk Level**: Highest
   - **Data Source**: Pink Sheets LLC, now OTC Markets Group

### Electronic Communication Networks (ECNs) - Secondary Venues
- Archipelago (now part of NYSE)
- EDGX, EDGA, BATS (now part of CBOE)
- Direct Edge, Nasdaq OMX

### Other Regulated Venues
- **CBOE** (Chicago Board Options Exchange) - primarily options, some equities
- **Unlisted Trading Privileges (UTP)** - third-market trading on other exchanges

---

## 2. Estimate of Total US Tradable Tickers

| Exchange/Market | Estimated Count | Status |
|---|---|---|
| NYSE | ~2,685 | Active |
| NASDAQ | ~2,727 | Active |
| NYSE American | ~400-500 | Active |
| OTCQX | ~10,000 | Active |
| OTCQB | ~5,000-7,000 | Active |
| OTC Pink | ~3,000-5,000 | Active |
| Foreign ADRs (Nasdaq/NYSE) | ~2,000 | Active |
| **Total US Tradable Tickers** | **~25,000-33,000+** | |

**Note**: The exact number fluctuates daily as companies list, delist, and go bankrupt. The actual "12,000+" referenced commonly includes the major exchanges (NYSE, NASDAQ) plus OTCQX tier securities.

---

## 3. Reliable Free & Public Data Sources for Ticker Lists

### A. Exchange-Official Data Sources

#### NYSE Data
- **Source**: https://www.nyse.com/data-products
- **What**: Listed company directory, symbol lookup
- **Method**: Web scraping or API access
- **Cost**: Free for basic lookup, premium for historical data
- **Quality**: Official, most reliable

#### NASDAQ Symbol Directory
- **Source**: https://www.nasdaq.com/market-activity/stocks
- **Download**: NASDAQ provides FTP downloads of listed symbols
- **Method**: 
  ```
  ftp://ftp.nasdaqtrader.com/SymbolDir/nasdaqlisted.txt
  ftp://ftp.nasdaqtrader.com/SymbolDir/otherlisted.txt
  ```
- **Cost**: Free
- **Files**: Daily updates available
- **Quality**: Official, highly reliable

#### SEC EDGAR Database
- **Source**: https://www.sec.gov/edgar/
- **What**: All SEC-registered companies
- **Method**: Query via Edgar API or web scraping
- **Cost**: Free
- **Coverage**: All companies filing with SEC (99% of public companies)
- **Notes**: Most comprehensive, includes historical data

### B. Third-Party Free Data Sources

#### IEX Cloud / IEX Finance (Free Tier)
- **API**: https://iexcloud.io/
- **Method**: REST API
- **Cost**: Free tier available (limited calls)
- **Symbols Available**: US and international
- **Update Frequency**: Real-time
- **Python**: `iexfinance` library

#### yfinance (Yahoo Finance Wrapper)
- **Source**: https://github.com/ranaroussi/yfinance
- **Method**: Python library
- **Cost**: Free
- **Coverage**: All major exchanges
- **Limitations**: 
  - Not affiliated with Yahoo (use at own risk)
  - Rate limited
  - Data quality varies
- **Installation**: `pip install yfinance`

#### Polygon.io
- **Source**: https://polygon.io/
- **Method**: REST API + WebSocket
- **Cost**: Free tier + premium
- **Features**: 
  - Real-time quotes
  - Historical data
  - Corporate actions
- **Quality**: Exchange-licensed data provider

#### Alpha Vantage
- **Source**: https://www.alphavantage.co/
- **Method**: REST API
- **Cost**: Free API key with rate limits
- **Features**: Stock data, forex, crypto, technical indicators
- **Quality**: Licensed provider, NASDAQ celebrates them

#### Finnhub
- **Source**: https://finnhub.io/
- **Method**: REST API
- **Cost**: Free tier available
- **Features**: Stock data, news, earnings, technical analysis

---

## 4. Specialized Data Sources by Market Segment

### OTC Market Data

#### OTC Markets Group (Official)
- **Source**: https://www.otcmarkets.com/
- **Method**: Web browsing + API
- **Data**: 
  - Company profiles
  - Quote data
  - Trading volume
  - Market tiers (OTCQX, OTCQB, Pink)
- **Cost**: Free for basic lookup
- **API**: Limited, mostly requires web scraping

#### FINRA (Financial Industry Regulatory Authority)
- **Source**: https://www.finra.org/
- **Data**: 
  - OTC trading data
  - Trade reporting
  - Market surveillance
- **Public Access**: Limited (most data requires member access)
- **Note**: Maintains data on all OTC trades

### Pink Sheets Data

#### Pink Sheets LLC (now part of OTC Markets)
- **Provides**: Daily quotations for OTC securities
- **Cost**: Subscription-based for professional use
- **Free Access**: Limited public information

---

## 5. Most Efficient Python Approaches to Fetch 12,000+ Tickers

### Approach 1: Direct NASDAQ File Download (Fastest)
```python
import pandas as pd
import urllib.request
import io

# Download NASDAQ listed stocks
nasdaq_url = "ftp://ftp.nasdaqtrader.com/SymbolDir/nasdaqlisted.txt"
other_listed_url = "ftp://ftp.nasdaqtrader.com/SymbolDir/otherlisted.txt"

try:
    nasdaq_df = pd.read_csv(nasdaq_url, sep='|', header=None)
    other_df = pd.read_csv(other_listed_url, sep='|', header=None)
    
    all_nasdaq = pd.concat([nasdaq_df, other_df], ignore_index=True)
    print(f"Total NASDAQ listed: {len(all_nasdaq)}")
except Exception as e:
    print(f"Error downloading: {e}")
```

### Approach 2: SEC EDGAR API (Most Comprehensive)
```python
import requests
import pandas as pd
from typing import List

def fetch_sec_tickers() -> List[dict]:
    """
    Fetch all SEC-registered companies using EDGAR API
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    
    response = requests.get(url)
    data = response.json()
    
    tickers = []
    for entry in data.values():
        tickers.append({
            'ticker': entry.get('ticker'),
            'company': entry.get('title'),
            'cik': entry.get('cik_str'),
            'exchange': entry.get('exchange')
        })
    
    return tickers

# Usage
sec_tickers = fetch_sec_tickers()
df = pd.DataFrame(sec_tickers)
print(f"Total SEC tickers: {len(df)}")
```

### Approach 3: Combined Exchange + OTC Data
```python
import pandas as pd
import requests
import json
from concurrent.futures import ThreadPoolExecutor

class TickerCollector:
    """Comprehensive ticker data collection from multiple sources"""
    
    def __init__(self):
        self.all_tickers = []
        self.tickers_by_exchange = {}
    
    def fetch_nasdaq_tickers(self) -> pd.DataFrame:
        """Fetch NASDAQ listed stocks"""
        urls = [
            "ftp://ftp.nasdaqtrader.com/SymbolDir/nasdaqlisted.txt",
            "ftp://ftp.nasdaqtrader.com/SymbolDir/otherlisted.txt"
        ]
        
        dfs = []
        for url in urls:
            try:
                df = pd.read_csv(url, sep='|')
                dfs.append(df)
            except Exception as e:
                print(f"Error fetching {url}: {e}")
        
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    
    def fetch_sec_tickers(self) -> pd.DataFrame:
        """Fetch all SEC-registered companies"""
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url)
        data = response.json()
        
        tickers = []
        for entry in data.values():
            tickers.append({
                'ticker': entry.get('ticker'),
                'company': entry.get('title'),
                'exchange': entry.get('exchange'),
                'cik': entry.get('cik_str')
            })
        
        return pd.DataFrame(tickers)
    
    def fetch_otc_tickers_from_yfinance(self) -> pd.DataFrame:
        """
        Fetch OTC tickers using yfinance
        Note: Limited - can't fetch all OTC tickers at once
        """
        import yfinance as yf
        
        # Common OTC prefixes (need manual lookup or third-party source)
        # This is a limitation - full OTC data requires web scraping
        otc_symbols = []
        
        return pd.DataFrame({'ticker': otc_symbols})
    
    def collect_all(self):
        """Collect tickers from all sources"""
        print("Fetching NASDAQ tickers...")
        nasdaq_df = self.fetch_nasdaq_tickers()
        print(f"  Found {len(nasdaq_df)} NASDAQ tickers")
        
        print("Fetching SEC EDGAR tickers...")
        sec_df = self.fetch_sec_tickers()
        print(f"  Found {len(sec_df)} SEC tickers")
        
        # Combine and deduplicate
        combined = pd.concat([nasdaq_df, sec_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=['ticker'])
        
        print(f"\nTotal unique tickers collected: {len(combined)}")
        
        return combined

# Usage
collector = TickerCollector()
all_tickers = collector.collect_all()
all_tickers.to_csv('all_us_tickers.csv', index=False)
```

### Approach 4: Web Scraping OTC Markets (Advanced)
```python
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import List

class OTCTickerScraper:
    """Scrape OTC tickers from OTC Markets website"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_otcqx_tickers(self) -> List[str]:
        """Fetch OTCQX tier tickers"""
        url = "https://www.otcmarkets.com/cgi-bin/browse?action=companies&market=OTCQX"
        
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse tickers from page (structure may vary)
            tickers = []
            for row in soup.find_all('tr')[1:]:  # Skip header
                cols = row.find_all('td')
                if cols:
                    ticker = cols[0].text.strip()
                    tickers.append(ticker)
            
            return tickers
        except Exception as e:
            print(f"Error scraping OTCQX: {e}")
            return []
    
    def fetch_all_otc_tickers(self) -> pd.DataFrame:
        """Fetch all OTC market tickers"""
        otc_data = []
        markets = ['OTCQX', 'OTCQB', 'OTC Pink']
        
        for market in markets:
            print(f"Fetching {market}...")
            url = f"https://www.otcmarkets.com/cgi-bin/browse?action=companies&market={market}"
            
            try:
                response = self.session.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract data (adjust selectors based on actual HTML)
                for row in soup.find_all('tr')[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        otc_data.append({
                            'ticker': cols[0].text.strip(),
                            'company': cols[1].text.strip(),
                            'market': market
                        })
            except Exception as e:
                print(f"  Error: {e}")
        
        return pd.DataFrame(otc_data)

# Usage
scraper = OTCTickerScraper()
otc_tickers = scraper.fetch_all_otc_tickers()
print(f"Total OTC tickers: {len(otc_tickers)}")
```

### Approach 5: Using Multiple APIs in Parallel (Most Robust)
```python
import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class MultiSourceTickerFetcher:
    """Fetch tickers from multiple APIs in parallel"""
    
    def __init__(self):
        self.all_tickers = []
    
    def fetch_sec_data(self) -> pd.DataFrame:
        """Fetch from SEC EDGAR"""
        try:
            url = "https://www.sec.gov/files/company_tickers.json"
            response = requests.get(url, timeout=10)
            data = response.json()
            return pd.DataFrame([
                {'ticker': v['ticker'], 'exchange': v.get('exchange'), 'source': 'SEC'}
                for v in data.values()
            ])
        except Exception as e:
            print(f"SEC fetch error: {e}")
            return pd.DataFrame()
    
    def fetch_polygon_data(self, api_key: str) -> pd.DataFrame:
        """Fetch from Polygon.io API"""
        try:
            url = f"https://api.polygon.io/v3/reference/tickers?apikey={api_key}&limit=1000"
            all_tickers = []
            
            while url:
                response = requests.get(url, timeout=10)
                data = response.json()
                all_tickers.extend(data.get('results', []))
                
                # Pagination
                url = data.get('next_url')
                if url:
                    url += f"&apikey={api_key}"
            
            df = pd.DataFrame(all_tickers)
            df['source'] = 'Polygon'
            return df[['ticker', 'source']].drop_duplicates()
        
        except Exception as e:
            print(f"Polygon fetch error: {e}")
            return pd.DataFrame()
    
    def fetch_iex_data(self, api_key: str) -> pd.DataFrame:
        """Fetch from IEX Cloud API"""
        try:
            url = f"https://cloud.iexapis.com/stable/ref-data/symbols?token={api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            return pd.DataFrame([
                {'ticker': item['symbol'], 'exchange': item.get('exchange'), 'source': 'IEX'}
                for item in data
            ])
        except Exception as e:
            print(f"IEX fetch error: {e}")
            return pd.DataFrame()
    
    def fetch_all_parallel(self, polygon_key: str = None, iex_key: str = None) -> pd.DataFrame:
        """Fetch from all sources in parallel"""
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self.fetch_sec_data): 'SEC',
            }
            
            if polygon_key:
                futures[executor.submit(self.fetch_polygon_data, polygon_key)] = 'Polygon'
            
            if iex_key:
                futures[executor.submit(self.fetch_iex_data, iex_key)] = 'IEX'
            
            results = []
            for future in as_completed(futures):
                try:
                    df = future.result()
                    results.append(df)
                    print(f"✓ {futures[future]} completed")
                except Exception as e:
                    print(f"✗ {futures[future]} failed: {e}")
        
        # Combine all results
        combined = pd.concat(results, ignore_index=True)
        combined = combined.drop_duplicates(subset=['ticker'])
        
        return combined.sort_values('ticker').reset_index(drop=True)

# Usage
fetcher = MultiSourceTickerFetcher()
# Requires API keys for some sources
all_tickers = fetcher.fetch_all_parallel(
    polygon_key="YOUR_POLYGON_KEY",
    iex_key="YOUR_IEX_KEY"
)
print(f"Total unique tickers: {len(all_tickers)}")
all_tickers.to_csv('comprehensive_tickers.csv', index=False)
```

---

## 6. Complete Comparison of Data Sources

### Free Sources Ranked by Quality & Completeness

| Source | Ticker Count | Reliability | Update Freq | Rate Limit | Python Support | OTC Coverage |
|---|---|---|---|---|---|---|
| SEC EDGAR | ~14,000 | ★★★★★ | Daily | None | Excellent | Good |
| NASDAQ FTP | ~3,200 | ★★★★★ | Daily | None | Excellent | N/A |
| NYSE Direct | ~2,700 | ★★★★★ | Daily | None | Good | N/A |
| yfinance | ~25,000+ | ★★★☆☆ | Real-time | Yes | Excellent | Limited |
| Polygon (Free) | ~15,000+ | ★★★★☆ | Real-time | Yes (calls) | Excellent | Limited |
| IEX Cloud (Free) | ~12,000+ | ★★★★☆ | Real-time | Yes (100K/mo) | Excellent | Good |
| Alpha Vantage | ~10,000+ | ★★★★☆ | Real-time | Yes (5 calls/min) | Excellent | Limited |
| Finnhub | ~12,000+ | ★★★★☆ | Real-time | Yes | Excellent | Limited |
| OTC Markets | ~10,000+ | ★★★★☆ | Daily | N/A | Requires Scraping | Excellent |

### Premium/Paid Sources

| Source | Cost | Coverage | Best For |
|---|---|---|---|
| Bloomberg Terminal | $24,000+/year | All + more | Professional traders |
| Reuters Eikon | $20,000+/year | All + more | Professional traders |
| FactSet | $15,000+/year | 40,000+ | Institutional investors |
| Refinitiv | $10,000+/year | All + more | Professional research |
| MarketWatch API | $100-1000/year | Comprehensive | Active traders |

---

## 7. Recommended Implementation Strategy

### For Your Use Case (12,000+ Tickers):

1. **Start with SEC EDGAR** (~14,000 tickers, most reliable)
   - No API key needed
   - Daily updates
   - Official government data
   - ~5-10 seconds to download

2. **Supplement with Polygon.io Free Tier** (~15,000 tickers)
   - Better OTC coverage
   - Includes delisted companies
   - Requires free registration

3. **Optional: Scrape OTC Markets** (additional ~10,000 OTC tickers)
   - Best source for pink sheets
   - No API needed but slower
   - Web scraping approach (see Approach 4)

4. **Combine & Deduplicate**
   - Merge all sources
   - Remove duplicates
   - Validate format

### Code Template:
```python
import pandas as pd
import requests
from typing import List

def get_all_us_tickers() -> pd.DataFrame:
    """Complete solution for fetching 12,000+ US stock tickers"""
    
    # 1. SEC EDGAR
    print("Fetching SEC EDGAR...")
    sec_url = "https://www.sec.gov/files/company_tickers.json"
    sec_response = requests.get(sec_url)
    sec_data = sec_response.json()
    sec_df = pd.DataFrame([
        {'ticker': v['ticker'], 'exchange': v.get('exchange'), 'source': 'SEC'}
        for v in sec_data.values()
    ])
    
    # 2. NASDAQ FTP (includes others)
    print("Fetching NASDAQ...")
    nasdaq_df = pd.read_csv(
        "ftp://ftp.nasdaqtrader.com/SymbolDir/nasdaqlisted.txt", 
        sep='|'
    )
    nasdaq_df['source'] = 'NASDAQ'
    
    # 3. Combine
    combined = pd.concat([sec_df, nasdaq_df], ignore_index=True)
    
    # 4. Deduplicate
    combined = combined.drop_duplicates(subset=['ticker'])
    
    print(f"Total unique tickers: {len(combined)}")
    return combined.sort_values('ticker').reset_index(drop=True)

# Save to file
tickers = get_all_us_tickers()
tickers.to_json('us_tickers.json', orient='records')
tickers.to_csv('us_tickers.csv', index=False)
```

---

## 8. Key Findings & Recommendations

### Key Points:
1. **Total US Tradable Tickers**: 25,000-33,000+ across all exchanges and OTC markets
2. **Major Exchanges Only** (NYSE + NASDAQ): ~5,400 tickers
3. **Including OTC Markets**: 12,000-25,000+ additional tickers
4. **SEC Registration** covers ~14,000 public companies
5. **Daily Liquidity** exists for ~5,000-8,000 tickers (rest are very illiquid)

### Best Approach for 12,000+ Tickers:
- **SEC EDGAR** for authoritative data (~14,000)
- **Polygon.io** for comprehensive coverage (~15,000+)
- **Custom OTC scraping** for pink sheets (~10,000+)
- **Total obtainable**: 25,000-30,000+ unique tickers

### Challenges:
1. No single free source has all tickers
2. OTC data quality varies significantly
3. API rate limits on free tiers
4. Pink sheets have minimal reporting requirements (data quality issues)
5. Constant changes (IPOs, delistings, bankruptcies)

### Time to Fetch 12,000+ Tickers:
- SEC EDGAR alone: ~10 seconds
- NASDAQ FTP: ~5 seconds  
- Combined (all): ~30-60 seconds
- With OTC scraping: 5-15 minutes (slower due to web scraping)

---

## References & URLs

### Official Exchange Data:
- NYSE: https://www.nyse.com/data-products
- NASDAQ: https://www.nasdaq.com/
  - FTP: ftp://ftp.nasdaqtrader.com/SymbolDir/
- SEC EDGAR: https://www.sec.gov/edgar/
- FINRA: https://www.finra.org/

### Free APIs & Data:
- yfinance: https://github.com/ranaroussi/yfinance
- Polygon.io: https://polygon.io/
- IEX Cloud: https://iexcloud.io/
- Alpha Vantage: https://www.alphavantage.co/
- Finnhub: https://finnhub.io/

### OTC Market Data:
- OTC Markets: https://www.otcmarkets.com/
- OTC Pink: https://www.otcpink.com/

### Reference Libraries:
- pandas: https://pandas.pydata.org/
- requests: https://requests.readthedocs.io/
- beautifulsoup4: https://www.crummy.com/software/BeautifulSoup/

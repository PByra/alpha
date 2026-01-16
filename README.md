# Alpha - Stock Market Analysis & Backtesting Platform

**Alpha** is a comprehensive Python-based desktop application for analyzing US stock market data and backtesting algorithmic trading strategies.

## Features

### 📊 Data Collection
- **S&P 500 Tickers** - Download ~500 major US companies
- **US Tradable Tickers** - Fetch ~5,000 actively traded stocks
- **All US Tickers** - Comprehensive ~12,000+ ticker list
- **30-Year Historical Data** - Up to 30 years of OHLCV data per stock
- **Smart Rate Limiting** - Exponential backoff to avoid API blocking
- **CSV Import** - Convert pre-packaged datasets to individual ticker JSON files

### 🔬 Analysis
- Real-time market data fetching
- Flexible data import from CSV sources
- OHLCV data processing and validation
- Per-ticker JSON storage for efficient access

### 📈 Backtesting
- Backtrader integration for strategy testing
- Professional-grade backtesting framework
- Support for custom trading strategies

### 🎛️ Dashboard
- PyQt5 desktop application
- Real-time status monitoring
- Detailed operation logs
- Multi-threaded background processing
- Results visualization

## Quick Start

### Prerequisites
- Python 3.10+
- Windows/macOS/Linux

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd alpha
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Launch Dashboard

```bash
python main.py
```

This opens the command center where you can:
- Fetch ticker lists
- Download historical data
- Import CSV files
- Monitor operations in real-time

## Project Structure

```
alpha/
├── main.py                      # Entry point
├── requirements.txt             # Package dependencies
├── CSV_IMPORT_GUIDE.md         # CSV import documentation
├── US_STOCK_EXCHANGES_RESEARCH.md  # Market research
│
├── app/
│   ├── __init__.py
│   └── dashboard.py             # PyQt5 GUI application
│
├── src/
│   ├── __init__.py
│   ├── scraper.py              # Data collection & CSV processing
│   ├── model.py                # ML models (placeholder)
│   └── analystics.py           # Data analysis tools
│
└── data/
    ├── raw/                    # Raw data downloads
    ├── processed/              # Per-ticker JSON files
    ├── sp500_tickers.json      # S&P 500 list
    ├── us_tradable_tickers.json # Major exchange tickers
    └── all_us_tickers.json     # Complete US ticker list
```

## Usage Guide

### 1. Fetch Tickers

Three options available:
- **S&P 500**: ~500 major companies
- **All US Tradable**: ~5,000 actively traded stocks
- **All US**: ~12,000+ total stocks

Click the corresponding button in the dashboard - tickers saved to JSON files.

### 2. Download Historical Data

**Recommended Approach:**
- Download pre-packaged CSV from Kaggle (e.g., "S&P 500 Stock Prices")
- Use CSV Import feature (see below)

**Direct Download:**
- Click "Download S&P 500 Data (30yr)" for fast 500-stock download
- Uses smart rate limiting to avoid API blocks

### 3. Import CSV Files (Recommended)

Most efficient method for large datasets:

```bash
# From GUI:
1. Click "Import CSV File" for single file
   or "Import CSV Folder" for batch processing
2. Select your CSV
3. Wait for conversion to complete
4. JSON files created in data/processed/

# From Code:
from src.scraper import StockDataScraper
scraper = StockDataScraper()
result = scraper.convert_csv_to_json("path/to/data.csv")
```

**Expected CSV Format:**
```csv
Date,Ticker,Open,High,Low,Close,Volume
2020-01-02,AAPL,73.45,75.19,73.19,75.09,135649300
2020-01-03,AAPL,74.29,74.74,73.48,74.36,106575600
```

See [CSV_IMPORT_GUIDE.md](CSV_IMPORT_GUIDE.md) for detailed documentation.

### 4. Access Data

```python
import json
from pathlib import Path

# Load converted ticker data
with open("data/processed/AAPL.json") as f:
    aapl_data = json.load(f)

print(f"AAPL: {aapl_data['data_points']} days of data")
print(f"Date range: {aapl_data['first_date']} to {aapl_data['last_date']}")
print(f"Latest close: ${aapl_data['historical_data'][-1]['close']}")
```

## Data Format

### Ticker JSON Structure

Each ticker gets an individual JSON file in `/data/processed/{TICKER}.json`:

```json
{
  "ticker": "AAPL",
  "data_points": 7500,
  "first_date": "1995-01-01",
  "last_date": "2025-01-15",
  "source": "market_data.csv",
  "converted_at": "2025-01-15 20:25:37",
  "historical_data": [
    {
      "date": "1995-01-01",
      "open": 25.50,
      "high": 26.00,
      "low": 25.25,
      "close": 25.75,
      "volume": 1000000
    }
  ]
}
```

## API Reference

### StockDataScraper Class

```python
from src.scraper import StockDataScraper

scraper = StockDataScraper()

# Fetch ticker lists
sp500 = scraper.get_sp500_tickers()          # ~500 tickers
us_tradable = scraper.get_us_tradable_tickers()  # ~5,000
all_us = scraper.get_all_us_tickers()        # ~12,000+

# Download 30 years of data
sp500_data = scraper.download_sp500_30years(delay=1.5)
us_data = scraper.download_us_tradable_30years(delay=1.5)
all_data = scraper.download_all_us_30years(delay=1.5)

# CSV Import
result = scraper.convert_csv_to_json("path/to/file.csv")
result = scraper.batch_convert_csv_folder("path/to/folder/")
```

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| S&P 500 Download | 12-15 min | 500 companies, 30 years |
| US Tradable Download | 1-2 hours | 5,000 stocks, 30 years |
| All US Download | 5-8+ hours | 12,000+ stocks, 30 years |
| CSV Import (1000 rows) | <1 second | Per-ticker processing |

## Rate Limiting

The scraper implements smart rate limiting:
- **Default delay**: 1.5 seconds between yfinance requests
- **HTTP 429 handling**: Exponential backoff (2s → 4s → 8s)
- **Max retries**: 3 attempts per ticker
- **Progress updates**: Every 100 tickers during bulk downloads

## Dependencies

Core packages:
- **PyQt5** - Desktop GUI framework
- **yfinance** - Yahoo Finance API
- **pandas** - Data processing
- **backtrader** - Backtesting framework

See [requirements.txt](requirements.txt) for complete list.

## Troubleshooting

### "Scraper not available"
Install missing dependencies:
```bash
pip install -r requirements.txt
```

### "Rate limited by yfinance"
The scraper automatically handles rate limiting. If still blocked:
- Try CSV import instead
- Increase delay parameter in download methods
- Check your internet connection

### "CSV column not found"
Check CSV format against [CSV_IMPORT_GUIDE.md](CSV_IMPORT_GUIDE.md)

### JSON files not created
- Check `/data/processed/` directory exists
- Verify write permissions on data folder
- Check conversion logs in dashboard

## Data Sources

### Recommended CSV Sources
1. **Kaggle** (Free) - Search "historical stock prices"
2. **Yahoo Finance** - Download via web interface
3. **EODData** (Paid) - Professional market data
4. **CRSP** (Academic) - Research database

### Free API
- yfinance - ~10 requests/second limit

## Future Enhancements

- [ ] Advanced technical indicators
- [ ] Machine learning models
- [ ] Real-time market alerts
- [ ] Portfolio tracking
- [ ] Risk analysis tools
- [ ] Options chain data
- [ ] Cryptocurrency support

## Contributing

Contributions welcome! Areas for improvement:
- Additional data sources
- UI/UX enhancements
- New analysis tools
- Performance optimizations

## License

This project is part of Alpha trading platform research.

## Contact

For questions or issues, please check:
- [CSV_IMPORT_GUIDE.md](CSV_IMPORT_GUIDE.md) - CSV import details
- [US_STOCK_EXCHANGES_RESEARCH.md](US_STOCK_EXCHANGES_RESEARCH.md) - Market research

---

**Status**: ✅ Production Ready for CSV Import & Data Analysis

**Last Updated**: January 15, 2025

# CSV Import Feature - Alpha Documentation

## Overview

The CSV import feature allows you to import pre-packaged market data from sources like Kaggle, EODData, or other CSV exports. This is the **recommended approach** for downloading large volumes of stock market data, as it's more efficient than downloading 12,000+ stocks individually.

## Features

✅ **Flexible CSV Detection** - Automatically detects column names (case-insensitive):
   - Date columns: `Date`, `date`, `DATE`, `Datetime`, `datetime`
   - Ticker columns: `Ticker`, `ticker`, `Symbol`, `symbol`, `TICKER`
   - OHLCV columns: `Open`, `High`, `Low`, `Close`, `Volume` (any case)

✅ **Automatic Ticker Extraction** - If no ticker column found, extracts from filename

✅ **Per-Ticker JSON Files** - Creates individual `{TICKER}.json` files in `/data/processed/`

✅ **Data Validation** - Validates date formats and OHLCV columns

✅ **Batch Processing** - Convert entire folders of CSV files at once

✅ **Progress Reporting** - Real-time status updates during conversion

✅ **Summary Reports** - JSON summary files track successful/failed conversions

## Usage

### Method 1: GUI Dashboard

1. **Launch the Dashboard:**
   ```bash
   python main.py
   ```

2. **Click "Import CSV File"** in the 📥 CSV Import section
   - Select a single CSV file
   - Conversion begins automatically
   - Results displayed in the Results tab

3. **Click "Import CSV Folder"** to process multiple CSVs
   - Select a folder containing CSV files
   - All CSVs processed sequentially
   - Status updates in Logs tab

### Method 2: Python Code

```python
from src.scraper import StockDataScraper

scraper = StockDataScraper()

# Convert single CSV file
result = scraper.convert_csv_to_json("path/to/market_data.csv")

# Convert entire folder
result = scraper.batch_convert_csv_folder("path/to/csv_folder/")
```

## Expected CSV Format

### Format 1: With Ticker Column (Recommended)

```csv
Date,Ticker,Open,High,Low,Close,Volume
2020-01-02,AAPL,73.45,75.19,73.19,75.09,135649300
2020-01-03,AAPL,74.29,74.74,73.48,74.36,106575600
2020-01-02,MSFT,158.67,160.41,157.92,160.04,23595800
```

### Format 2: Without Ticker Column (Uses Filename)

**File:** `AAPL.csv`
```csv
Date,Open,High,Low,Close,Volume
2020-01-02,73.45,75.19,73.19,75.09,135649300
2020-01-03,74.29,74.74,73.48,74.36,106575600
```

## Output Structure

Each ticker creates a JSON file in `/data/processed/{TICKER}.json`:

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
    },
    ...
  ]
}
```

## Data Source Recommendations

### Where to Get CSV Data

1. **Kaggle** (Free)
   - Search: "historical stock data"
   - Usually includes 500-5000 stocks
   - Download formats: Single CSV or per-ticker CSVs

2. **Yahoo Finance** (Free, Manual Export)
   - Download via yfinance or web interface
   - Format your own CSV using provided structure

3. **EODData** (Paid)
   - Professional historical market data
   - Bulk download capabilities
   - Comprehensive US stock coverage

4. **CRSP** (Academic)
   - Professional research database
   - If you have institutional access

## Example Usage

### Download from Kaggle

1. Go to https://www.kaggle.com/ and search "historical stock prices"
2. Download a dataset (e.g., "S&P 500 Stock Prices 1950-2024")
3. Extract the CSV file(s)
4. In Alpha Dashboard, click "Import CSV Folder"
5. Select the folder
6. Wait for conversion to complete

### Verify Converted Data

```python
import json
from pathlib import Path

# Check converted file
ticker_file = Path("data/processed/AAPL.json")
with open(ticker_file) as f:
    data = json.load(f)

print(f"Ticker: {data['ticker']}")
print(f"Data points: {data['data_points']}")
print(f"Date range: {data['first_date']} to {data['last_date']}")
print(f"Sample prices: {data['historical_data'][:3]}")
```

## Return Format

### Success Response

```python
{
    "successful_tickers": 4,
    "failed_tickers": 0,
    "total_tickers": 4,
    "total_data_points": 12,
    "source_file": "test_market_data.csv",
    "conversion_time": "2025-01-15 20:25:37",
    "success_rate": "100.0%",
    "tickers_created": ["AAPL", "MSFT", "GOOGL", "TSLA"]
}
```

### Error Response

```python
{
    "error": "Date column not found",
    "successful_tickers": 0,
    "failed_tickers": 0
}
```

## Column Name Variations Supported

| Data Type | Supported Names |
|-----------|-----------------|
| **Date** | Date, date, DATE, Datetime, datetime |
| **Ticker** | Ticker, ticker, Symbol, symbol, TICKER |
| **Open** | Open, open, OPEN, O |
| **High** | High, high, HIGH, H |
| **Low** | Low, low, LOW, L |
| **Close** | Close, close, CLOSE, C, Adj Close |
| **Volume** | Volume, volume, VOLUME, Vol, Volsume |

## Integration with Backtrader

Once you have converted your CSVs to JSON format, you can use them with Backtrader:

```python
import json
from pathlib import Path
import backtrader as bt

# Load converted JSON data
ticker = "AAPL"
with open(f"data/processed/{ticker}.json") as f:
    data = json.load(f)

# Convert to Backtrader format
# (Details in Backtrader integration docs)
```

## Performance

- **Speed**: ~1000 data points per second on modern hardware
- **Memory**: Streaming processing, minimal RAM usage
- **Scalability**: Tested with 100+ ticker files in batch

## Troubleshooting

### "Date column not found"
- Ensure your CSV has a column named: Date, date, or DATE
- Check column names for typos

### "No data found for ticker"
- Verify ticker column spelling matches CSV
- Check for empty rows in CSV

### "Volume column missing"
- Volume is optional; conversion continues
- Price data will be included without volume

### Files not appearing in /data/processed/
- Check permissions on data/ directory
- Ensure disk space available
- Check conversion logs for errors

## Next Steps

1. ✅ Convert your CSV data using this feature
2. → Use JSON files for backtesting
3. → Implement trading strategies
4. → Analyze performance metrics

## See Also

- [Scraper Documentation](../src/scraper.py) - Detailed scraper API
- [Dashboard Guide](../app/dashboard.py) - GUI usage
- [Backtrader Integration](../docs/backtrader_setup.md) - Backtesting setup

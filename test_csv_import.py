#!/usr/bin/env python3
"""
Test script to validate CSV to JSON conversion functionality
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scraper import StockDataScraper

def test_csv_conversion():
    """Test converting a CSV file to JSON format"""
    scraper = StockDataScraper()
    
    # Test single CSV file conversion
    csv_file = Path("test_market_data.csv")
    if csv_file.exists():
        print(f"\n📊 Testing CSV conversion for: {csv_file.name}")
        print("=" * 60)
        
        result = scraper.convert_csv_to_json(str(csv_file))
        
        print(f"\n✓ Conversion Result:")
        print(f"  - Successful tickers: {result.get('successful_tickers', 0)}")
        print(f"  - Failed tickers: {result.get('failed_tickers', 0)}")
        print(f"  - Total data points processed: {result.get('total_data_points', 0)}")
        
        if result.get('successful_tickers', 0) > 0:
            print(f"\n✓ Successfully converted tickers:")
            for ticker in result.get('tickers_created', []):
                ticker_json = Path("data/processed") / f"{ticker}.json"
                if ticker_json.exists():
                    size = ticker_json.stat().st_size
                    print(f"  - {ticker}: {size} bytes")
        
        if result.get('failed_tickers', 0) > 0:
            print(f"\n⚠️ Failed tickers:")
            for ticker, error in result.get('failed_conversions', {}).items():
                print(f"  - {ticker}: {error}")
        
        print("\n" + "=" * 60)
        return True
    else:
        print(f"❌ CSV file not found: {csv_file}")
        return False

if __name__ == "__main__":
    success = test_csv_conversion()
    sys.exit(0 if success else 1)

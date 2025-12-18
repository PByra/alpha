#Functions related to api calls and web scraping, this is our data collection hub
#simple testing
import yfinance as yf

def grab_stock_data(ticker):
    """Fetch historical stock data for a given ticker symbol."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1mo")
    return hist

if __name__ == "__main__":
    data = grab_stock_data("AAPL")
    print(data)
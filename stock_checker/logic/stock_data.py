import yfinance as yf
import pandas as pd
import numpy as np

class StockData:
    def __init__(self, ticker):
        self.ticker_symbol = ticker
        self.ticker = yf.Ticker(ticker)
        self.hist = None
        self.info = None

    def fetch_data(self):
        """Fetch historical data and basic info."""
        # fix: auto_adjust=True to handle splits/dividends, though for simple close price check it might be fine.
        # Getting 1 year of data for Beta calculation
        self.hist = self.ticker.history(period="1y")
        self.info = self.ticker.info

    def get_current_price(self):
        if self.hist is not None and not self.hist.empty:
            return self.hist['Close'].iloc[-1]
        return None

    def get_company_name(self):
        """Return the company name if available."""
        if self.info:
            return self.info.get("longName") or self.info.get("shortName") or self.ticker_symbol
        return self.ticker_symbol

    # --- Short-term Strategy Metrics ---

    def calculate_beta(self, benchmark_ticker="^N225"):
        """Calculate Beta relative to a benchmark (default: Nikkei 225) using last 20 days."""
        if self.hist is None or self.hist.empty:
            return None
        
        # We need benchmark data aligned with stock data
        benchmark = yf.Ticker(benchmark_ticker)
        # Fetch slightly more than 20 days to ensure overlap
        bench_hist = benchmark.history(period="3mo")

        # Calculate daily returns
        stock_returns = self.hist['Close'].pct_change().dropna()
        bench_returns = bench_hist['Close'].pct_change().dropna()

        # Align metrics
        df = pd.DataFrame({'stock': stock_returns, 'benchmark': bench_returns}).dropna()
        
        # Use last 20 days of overlapping data
        df_last20 = df.tail(20)
        
        if len(df_last20) < 10: # Not enough data
            return None

        # Covariance / Variance
        covariance = df_last20['stock'].cov(df_last20['benchmark'])
        variance = df_last20['benchmark'].var()
        
        if variance == 0:
            return None
            
        return covariance / variance

    def calculate_rsi(self, window=14):
        """Calculate RSI (14 days)."""
        if self.hist is None or len(self.hist) < window + 1:
            return None

        delta = self.hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    def check_volume_surge(self):
        """Check if recent volume is 1.5x of 5-day average."""
        if self.hist is None or len(self.hist) < 6:
            return None

        recent_volume = self.hist['Volume'].iloc[-1]
        avg_volume_5d = self.hist['Volume'].iloc[-6:-1].mean()

        if avg_volume_5d == 0:
            return False

        return recent_volume >= (avg_volume_5d * 1.5)

    # --- Medium-term Strategy Metrics ---

    def get_fundamentals(self):
        """Extract needed fundamental metrics."""
        if not self.info:
            return {}

        return {
            "roe": self.info.get("returnOnEquity"),
            "per": self.info.get("trailingPE"),
            "pb_ratio": self.info.get("priceToBook"), # Optional bonus
            "total_assets": self.info.get("totalAssets"),
            "total_equity": self.info.get("totalStockholderEquity"),
            "revenue_growth": self.info.get("revenueGrowth"),
            "market_cap": self.info.get("marketCap")
        }

    def calculate_equity_ratio(self):
        """Calculate Equity Ratio (Total Equity / Total Assets)."""
        funds = self.get_fundamentals()
        equity = funds.get("total_equity")
        assets = funds.get("total_assets")

        if equity is not None and assets is not None and assets > 0:
            return equity / assets
        return None

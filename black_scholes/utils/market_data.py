"""Market data utilities for Black-Scholes option pricing.

This module provides functions for fetching and processing market data,
including stock prices, volatility calculations, and risk-free rates.
"""

import yfinance as yf
import numpy as np
from datetime import datetime
from typing import Tuple, List, Optional

def get_stock_data(ticker: str, period: str = "1y") -> Tuple[float, float]:
    """Fetch current stock price and calculate historical volatility.

    Args:
        ticker: Stock ticker symbol
        period: Time period for historical data (default: "1y")

    Returns:
        Tuple[float, float]: Current stock price and annualized volatility

    Raises:
        ValueError: If ticker is invalid or data cannot be fetched
    """
    try:
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period=period)
        
        if hist_data.empty:
            raise ValueError(f"No data available for ticker {ticker}")
        
        current_price = hist_data['Close'].iloc[-1]
        returns = hist_data['Close'].pct_change().dropna()
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        
        return current_price, volatility
    except Exception as e:
        raise ValueError(f"Error fetching data for {ticker}: {str(e)}")

def get_option_chain(ticker: str, expiry_date: Optional[str] = None) -> dict:
    """Fetch option chain data for a given stock and expiration date.

    Args:
        ticker: Stock ticker symbol
        expiry_date: Option expiration date (YYYY-MM-DD). If None, uses nearest expiry.

    Returns:
        dict: Dictionary containing call and put option data

    Raises:
        ValueError: If ticker is invalid or data cannot be fetched
    """
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        
        if not expirations:
            raise ValueError(f"No option data available for {ticker}")
        
        if expiry_date is None:
            expiry_date = expirations[0]
        elif expiry_date not in expirations:
            raise ValueError(f"Invalid expiry date. Available dates: {expirations}")
        
        options_chain = stock.option_chain(expiry_date)
        
        return {
            "calls": options_chain.calls,
            "puts": options_chain.puts,
            "expiry": expiry_date
        }
    except Exception as e:
        raise ValueError(f"Error fetching option chain for {ticker}: {str(e)}")

def get_risk_free_rate() -> float:
    """Get the current risk-free rate (approximated using 10-Year Treasury yield).

    Returns:
        float: Current risk-free rate as a decimal
    """
    try:
        treasury = yf.Ticker("^TNX")  # 10-Year Treasury yield
        current_rate = treasury.history(period="1d")['Close'].iloc[-1]
        return current_rate / 100  # Convert percentage to decimal
    except Exception:
        return 0.04  # Default to 4% if data cannot be fetched

def calculate_time_to_expiry(expiry_date: str) -> float:
    """Calculate time to expiration in years.

    Args:
        expiry_date: Option expiration date (YYYY-MM-DD)

    Returns:
        float: Time to expiration in years
    """
    try:
        today = datetime.today()
        expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
        days_to_expiry = (expiry - today).days
        
        if days_to_expiry < 0:
            raise ValueError("Expiry date must be in the future")
        
        return days_to_expiry / 365
    except ValueError as e:
        raise ValueError(f"Invalid expiry date format: {str(e)}") 
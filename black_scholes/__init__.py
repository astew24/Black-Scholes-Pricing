"""Black-Scholes option pricing package.

This package provides tools for calculating option prices and Greeks using the
Black-Scholes model, along with utilities for market data and visualization.
"""

from .core.pricing import black_scholes, calculate_greeks
from .utils.market_data import (
    get_stock_data,
    get_option_chain,
    get_risk_free_rate,
    calculate_time_to_expiry
)
from .visualization.plots import plot_price_sensitivity, plot_greeks

__version__ = "0.1.0"
__all__ = [
    "black_scholes",
    "calculate_greeks",
    "get_stock_data",
    "get_option_chain",
    "get_risk_free_rate",
    "calculate_time_to_expiry",
    "plot_price_sensitivity",
    "plot_greeks"
]

"""Core Black-Scholes option pricing implementation.

This module contains the core implementation of the Black-Scholes option pricing model
for European call and put options.
"""

import numpy as np
from scipy.stats import norm
from typing import Literal, Union, Tuple

OptionType = Literal["call", "put"]

def black_scholes(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType = "call"
) -> float:
    """Price a European call or put using the Black-Scholes formula.

    spot_price and strike_price in the same currency; time_to_expiry in years;
    volatility and risk_free_rate as decimals (e.g. 0.25 = 25%).
    """
    # Input validation
    # Note: risk_free_rate can be negative (e.g. some EUR curves) — not validated here.
    if spot_price <= 0:
        raise ValueError("Spot price must be positive")
    if strike_price <= 0:
        raise ValueError("Strike price must be positive")
    if time_to_expiry <= 0:
        raise ValueError("Time to expiry must be positive")
    if volatility <= 0:
        raise ValueError("Volatility must be positive")
    if not isinstance(option_type, str) or option_type.lower() not in ["call", "put"]:
        raise ValueError("Option type must be either 'call' or 'put'")

    # Calculate d1 and d2
    d1 = (np.log(spot_price / strike_price) + 
          (risk_free_rate + (volatility**2) / 2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)

    # Calculate option price
    if option_type.lower() == "call":
        price = (spot_price * norm.cdf(d1) - 
                strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2))
    else:  # put
        price = (strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2) - 
                spot_price * norm.cdf(-d1))
    
    return price

def calculate_greeks(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    option_type: OptionType = "call"
) -> dict:
    """Compute delta, gamma, theta, vega, rho for a European option.

    Theta is per calendar day (divided by 365) — matches what most platforms show.
    Vega is per 1-unit vol move; divide by 100 if you want per 1 percentage-point.
    """
    # Input validation
    if spot_price <= 0:
        raise ValueError("Spot price must be positive")
    if strike_price <= 0:
        raise ValueError("Strike price must be positive")
    if time_to_expiry <= 0:
        raise ValueError("Time to expiry must be positive")
    if volatility <= 0:
        raise ValueError("Volatility must be positive")

    d1 = (np.log(spot_price / strike_price) + 
          (risk_free_rate + (volatility**2) / 2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
    d2 = d1 - volatility * np.sqrt(time_to_expiry)

    # Calculate Greeks
    if option_type.lower() == "call":
        delta = norm.cdf(d1)
        theta = (-spot_price * norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry)) -
                risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2))
        rho = strike_price * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(d2)
    else:  # put
        delta = norm.cdf(d1) - 1
        theta = (-spot_price * norm.pdf(d1) * volatility / (2 * np.sqrt(time_to_expiry)) +
                risk_free_rate * strike_price * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2))
        rho = -strike_price * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * norm.cdf(-d2)

    theta = theta / 365  # convert to per-calendar-day (market convention)

    # Common Greeks for both call and put (identical by definition)
    # Vega returned in price units per 1-unit vol move; divide by 100 for per-1%-point
    gamma = norm.pdf(d1) / (spot_price * volatility * np.sqrt(time_to_expiry))
    vega = spot_price * np.sqrt(time_to_expiry) * norm.pdf(d1)

    return {
        "delta": delta,
        "gamma": gamma,
        "theta": theta,
        "vega": vega,
        "rho": rho
    }


def implied_volatility(
    market_price: float,
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    option_type: OptionType = "call",
    tol: float = 1e-6,
    max_iterations: int = 100,
) -> float:
    """Back out implied vol from a market price using Brent's method.

    Searches vol in [1e-6, 10.0]. Raises ValueError if the market price
    is outside the no-arbitrage bounds (usually means the price is stale
    or the params are wrong).
    """
    from scipy.optimize import brentq

    def objective(sigma: float) -> float:
        return black_scholes(spot_price, strike_price, time_to_expiry,
                             risk_free_rate, sigma, option_type) - market_price

    try:
        return brentq(objective, 1e-6, 10.0, xtol=tol, maxiter=max_iterations)
    except ValueError:
        raise ValueError(
            f"No implied volatility found for market_price={market_price:.4f}. "
            "Price may be outside the no-arbitrage bounds."
        )
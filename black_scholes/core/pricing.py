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
    """Calculate the price of a European option using the Black-Scholes formula.

    Args:
        spot_price: Current price of the underlying asset (S)
        strike_price: Strike price of the option (K)
        time_to_expiry: Time to expiration in years (T)
        risk_free_rate: Risk-free interest rate as a decimal (r)
        volatility: Volatility of the underlying asset (σ)
        option_type: Type of option, either "call" or "put"

    Returns:
        float: The theoretical price of the option

    Raises:
        ValueError: If option_type is not "call" or "put"
        ValueError: If any of the input parameters are invalid
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
    """Calculate the option Greeks (delta, gamma, theta, vega, rho).

    Args:
        spot_price: Current price of the underlying asset (S)
        strike_price: Strike price of the option (K)
        time_to_expiry: Time to expiration in years (T)
        risk_free_rate: Risk-free interest rate as a decimal (r)
        volatility: Volatility of the underlying asset (σ)
        option_type: Type of option, either "call" or "put"

    Returns:
        dict: Dictionary containing the option Greeks
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
    """Back out implied volatility from an observed market price using Brent's method.

    Args:
        market_price: Observed market price of the option
        spot_price: Current price of the underlying asset (S)
        strike_price: Strike price of the option (K)
        time_to_expiry: Time to expiration in years (T)
        risk_free_rate: Risk-free interest rate as a decimal (r)
        option_type: Type of option, either "call" or "put"
        tol: Tolerance for the root-finding convergence
        max_iterations: Maximum number of Brent iterations

    Returns:
        float: Implied volatility as a decimal (e.g. 0.25 = 25%)

    Raises:
        ValueError: If no implied volatility exists for the given market price
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
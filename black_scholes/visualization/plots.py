"""Visualization utilities for Black-Scholes option pricing.

This module provides functions for creating various plots related to
option pricing, including price sensitivity analysis and Greeks visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
from ..core.pricing import black_scholes, calculate_greeks

def plot_price_sensitivity(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    parameter: str = "volatility",
    parameter_range: Optional[Tuple[float, float]] = None,
    n_points: int = 50
) -> None:
    """Plot option price sensitivity to various parameters.

    Args:
        spot_price: Current price of the underlying asset
        strike_price: Strike price of the option
        time_to_expiry: Time to expiration in years
        risk_free_rate: Risk-free interest rate
        volatility: Volatility of the underlying asset
        parameter: Parameter to analyze ("volatility", "time", "spot", or "strike")
        parameter_range: Range of parameter values to plot (min, max)
        n_points: Number of points to plot

    Raises:
        ValueError: If parameter is invalid or parameter_range is invalid
    """
    if parameter not in ["volatility", "time", "spot", "strike"]:
        raise ValueError("Parameter must be one of: volatility, time, spot, strike")

    if parameter_range is None:
        if parameter == "volatility":
            parameter_range = (0.1, 1.0)
        elif parameter == "time":
            parameter_range = (0.01, 1.0)
        elif parameter == "spot":
            parameter_range = (strike_price * 0.5, strike_price * 1.5)
        else:  # strike
            parameter_range = (spot_price * 0.5, spot_price * 1.5)

    param_values = np.linspace(parameter_range[0], parameter_range[1], n_points)
    call_prices = []
    put_prices = []

    for value in param_values:
        kwargs = {
            "spot_price": spot_price,
            "strike_price": strike_price,
            "time_to_expiry": time_to_expiry,
            "risk_free_rate": risk_free_rate,
            "volatility": volatility
        }
        kwargs[parameter] = value

        call_prices.append(black_scholes(**kwargs, option_type="call"))
        put_prices.append(black_scholes(**kwargs, option_type="put"))

    plt.figure(figsize=(10, 6))
    plt.plot(param_values, call_prices, label="Call Option", color='blue')
    plt.plot(param_values, put_prices, label="Put Option", color='red')
    plt.xlabel(f"{parameter.capitalize()}")
    plt.ylabel("Option Price")
    plt.title(f"Option Price Sensitivity to {parameter.capitalize()}")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_greeks(
    spot_price: float,
    strike_price: float,
    time_to_expiry: float,
    risk_free_rate: float,
    volatility: float,
    parameter: str = "spot",
    parameter_range: Optional[Tuple[float, float]] = None,
    n_points: int = 50
) -> None:
    """Plot option Greeks sensitivity to various parameters.

    Args:
        spot_price: Current price of the underlying asset
        strike_price: Strike price of the option
        time_to_expiry: Time to expiration in years
        risk_free_rate: Risk-free interest rate
        volatility: Volatility of the underlying asset
        parameter: Parameter to analyze ("spot", "time", or "volatility")
        parameter_range: Range of parameter values to plot (min, max)
        n_points: Number of points to plot

    Raises:
        ValueError: If parameter is invalid or parameter_range is invalid
    """
    if parameter not in ["spot", "time", "volatility"]:
        raise ValueError("Parameter must be one of: spot, time, volatility")

    if parameter_range is None:
        if parameter == "spot":
            parameter_range = (strike_price * 0.5, strike_price * 1.5)
        elif parameter == "time":
            parameter_range = (0.01, 1.0)
        else:  # volatility
            parameter_range = (0.1, 1.0)

    param_values = np.linspace(parameter_range[0], parameter_range[1], n_points)
    greeks = {
        "delta": {"call": [], "put": []},
        "gamma": [],
        "theta": {"call": [], "put": []},
        "vega": [],
        "rho": {"call": [], "put": []}
    }

    for value in param_values:
        kwargs = {
            "spot_price": spot_price,
            "strike_price": strike_price,
            "time_to_expiry": time_to_expiry,
            "risk_free_rate": risk_free_rate,
            "volatility": volatility
        }
        kwargs[parameter] = value

        # Calculate Greeks for both call and put
        call_greeks = calculate_greeks(**kwargs, option_type="call")
        put_greeks = calculate_greeks(**kwargs, option_type="put")

        # Store values
        greeks["delta"]["call"].append(call_greeks["delta"])
        greeks["delta"]["put"].append(put_greeks["delta"])
        greeks["gamma"].append(call_greeks["gamma"])  # Same for calls and puts
        greeks["theta"]["call"].append(call_greeks["theta"])
        greeks["theta"]["put"].append(put_greeks["theta"])
        greeks["vega"].append(call_greeks["vega"])  # Same for calls and puts
        greeks["rho"]["call"].append(call_greeks["rho"])
        greeks["rho"]["put"].append(put_greeks["rho"])

    # Create subplots for each Greek
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(f"Option Greeks Sensitivity to {parameter.capitalize()}")

    # Plot each Greek
    for i, (greek, values) in enumerate(greeks.items()):
        row = i // 3
        col = i % 3
        ax = axes[row, col]

        if greek in ["gamma", "vega"]:
            ax.plot(param_values, values, label=greek.capitalize())
        else:
            ax.plot(param_values, values["call"], label=f"Call {greek.capitalize()}")
            ax.plot(param_values, values["put"], label=f"Put {greek.capitalize()}")

        ax.set_xlabel(parameter.capitalize())
        ax.set_ylabel(greek.capitalize())
        ax.grid(True)
        ax.legend()

    plt.tight_layout()
    plt.show() 
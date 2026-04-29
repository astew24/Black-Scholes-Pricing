# Black-Scholes Option Pricing

**[Live Demo →](https://astew24.github.io/Black-Scholes-Pricing/)**

Python implementation of the Black-Scholes model for European options — price, Greeks, and implied volatility. Includes a Streamlit app for interactive exploration and a CLI for quick calculations against live market data.

## Quick start

```python
from black_scholes.core.pricing import black_scholes, calculate_greeks, implied_volatility

price = black_scholes(spot_price=150, strike_price=155, time_to_expiry=0.25,
                      risk_free_rate=0.05, volatility=0.25, option_type="call")

greeks = calculate_greeks(150, 155, 0.25, 0.05, 0.25, "call")
# greeks["theta"] is per calendar day (market convention)

iv = implied_volatility(market_price=5.20, spot_price=150, strike_price=155,
                        time_to_expiry=0.25, risk_free_rate=0.05)
```

## What's included

- Black-Scholes pricing for European calls and puts
- Greeks: delta, gamma, theta (per calendar day), vega, rho
- Implied volatility via Brent's method — works on any liquid option
- CLI: `black-scholes AAPL --plot` pulls live data from yfinance and prices the ATM option
- Streamlit app for sensitivity curves and payoff diagrams
- Put-call parity and Greeks sign tests

## Setup

```bash
git clone https://github.com/astew24/Black-Scholes-Pricing.git
cd Black-Scholes-Pricing
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

```bash
# Run tests
pytest black_scholes/tests/

# CLI
black-scholes AAPL --strike 150 --expiry 2025-06-20

# Streamlit
streamlit run black_scholes/streamlit/app.py
```

## Limitations

Black-Scholes assumes constant volatility and no dividends. It's fine for rough European option pricing but don't use it to model anything with early exercise or a vol surface.

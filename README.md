# Black-Scholes Option Pricing

A Python package for calculating option prices and Greeks using the Black-Scholes model, with support for real market data integration and interactive visualization.

## Features

- **Core Pricing Engine**
  - Black-Scholes formula implementation for European options
  - Greeks calculation (delta, gamma, theta, vega, rho)
  - Input validation and error handling

- **Market Data Integration**
  - Real-time stock price and volatility data using yfinance
  - Option chain data fetching
  - Risk-free rate approximation using Treasury yields

- **Multiple Interfaces**
  - Command-line interface (CLI)
  - Interactive web interface using Streamlit
  - Python API for programmatic use

- **Visualization Tools**
  - Price sensitivity analysis
  - Greeks sensitivity plots
  - Interactive parameter adjustment

- **Educational Resources**
  - Jupyter notebook tutorial
  - Comprehensive documentation
  - Example usage scenarios

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/black-scholes-pricing.git
cd black-scholes-pricing
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

## Usage

### Command Line Interface

Calculate option prices for a stock:
```bash
black-scholes AAPL --plot
```

Additional options:
```bash
black-scholes AAPL --strike 150 --expiry 2024-12-20 --volatility 0.3 --risk-free-rate 0.05
```

### Streamlit Web Interface

Launch the interactive web interface:
```bash
streamlit run black_scholes/streamlit/app.py
```

### Python API

```python
from black_scholes import black_scholes, calculate_greeks

# Calculate option price
price = black_scholes(
    spot_price=100,
    strike_price=100,
    time_to_expiry=1.0,
    risk_free_rate=0.05,
    volatility=0.2,
    option_type="call"
)

# Calculate Greeks
greeks = calculate_greeks(
    spot_price=100,
    strike_price=100,
    time_to_expiry=1.0,
    risk_free_rate=0.05,
    volatility=0.2,
    option_type="call"
)
```

### Jupyter Notebook Tutorial

Run the educational notebook:
```bash
jupyter notebook black_scholes/examples/notebooks/black_scholes_tutorial.ipynb
```

## Development

### Running Tests

```bash
pytest black_scholes/tests/
```

### Project Structure

```
black_scholes/
├── core/
│   └── pricing.py          # Core pricing logic
├── utils/
│   └── market_data.py      # Market data utilities
├── visualization/
│   └── plots.py           # Plotting functions
├── cli/
│   └── main.py            # Command-line interface
├── streamlit/
│   └── app.py             # Web interface
├── tests/
│   └── test_pricing.py    # Unit tests
└── examples/
    └── notebooks/         # Jupyter notebooks
```

## Dependencies

- numpy >= 1.21.0
- scipy >= 1.7.0
- pandas >= 1.3.0
- matplotlib >= 3.4.0
- yfinance >= 0.1.70
- streamlit >= 1.0.0
- pytest >= 6.2.5
- jupyter >= 1.0.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Black-Scholes model by Fischer Black and Myron Scholes
- yfinance for market data access
- Streamlit for the web interface framework



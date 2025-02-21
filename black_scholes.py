import numpy as np
import yfinance as yf
from scipy.stats import norm
from datetime import datetime
import matplotlib.pyplot as plt

def black_scholes(S, K, T, r, sigma, option_type="call"):
    """
    Black-Scholes formula for pricing european call and put options 
    
    S = Current stock price
    K = Strike price
    T = Time to expiration (in years)
    r = Risk-free interest rate (as a decimal)
    sigma = Volatility of the stock
    option_type = "call" or "put"
    """
    d1 = (np.log(S / K) + (r + (sigma**2) / 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")
    
    return price


# Select a stock ticker (e.g., Apple - AAPL)
ticker = "AAPL"
stock = yf.Ticker(ticker)

# Get current stock price
S0 = stock.history(period="1d")['Close'].values[0]

# Get options expiration dates
expirations = stock.options
selected_expiry = expirations[0]  # Select nearest expiration

# Get options chain
options_chain = stock.option_chain(selected_expiry)

# Choose a strike price (closest to current stock price)
K = options_chain.calls['strike'].iloc[0]

# Set risk-free rate (approximate from US 10-Year Treasury)
r = 0.04  # 4% risk-free rate

# Compute time to expiration in years
today = datetime.today()
expiry_date = datetime.strptime(selected_expiry, "%Y-%m-%d")
T = (expiry_date - today).days / 365  # Convert days to years

# Calculate historical volatility
hist_data = stock.history(period="1y")
hist_data['Returns'] = hist_data['Close'].pct_change()
sigma = np.std(hist_data['Returns']) * np.sqrt(252)  # Annualized volatility

# Print collected values
print(f"Stock Price (S0): ${S0:.2f}")
print(f"Strike Price (K): ${K:.2f}")
print(f"Time to Expiry (T): {T:.3f} years")
print(f"Risk-Free Rate (r): {r}")
print(f"Estimated Volatility (σ): {sigma:.4f}")

# Compute Black-Scholes Prices
call_price = black_scholes(S0, K, T, r, sigma, "call")
put_price = black_scholes(S0, K, T, r, sigma, "put")

print(f"\nBlack-Scholes Call Option Price: ${call_price:.2f}")
print(f"Black-Scholes Put Option Price: ${put_price:.2f}")

# Get real market option prices
market_call_price = options_chain.calls.loc[options_chain.calls['strike'] == K, 'lastPrice'].values[0]
market_put_price = options_chain.puts.loc[options_chain.puts['strike'] == K, 'lastPrice'].values[0]

print(f"\nMarket Call Option Price: ${market_call_price:.2f}")
print(f"Market Put Option Price: ${market_put_price:.2f}")

volatilities = np.linspace(0.1, 1, 50)  # Test different volatilities
call_prices = [black_scholes(S0, K, T, r, v, "call") for v in volatilities]
put_prices = [black_scholes(S0, K, T, r, v, "put") for v in volatilities]

plt.figure(figsize=(10, 5))
plt.plot(volatilities, call_prices, label="Call Option Price", color='blue')
plt.plot(volatilities, put_prices, label="Put Option Price", color='red')
plt.xlabel("Volatility (σ)")
plt.ylabel("Option Price")
plt.title("Impact of Volatility on Option Prices")
plt.legend()
plt.show()

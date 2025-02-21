**# Black-Scholes Option Pricing Model**  

This project implements the **Black-Scholes Model** to calculate the theoretical prices of **European call and put options**. It fetches real-time stock data, calculates historical volatility, and compares model-predicted prices with actual market prices.

## **How It Works**  
1. Fetches **real-time stock data** from Yahoo Finance (`yfinance`).  
2. Retrieves **option chain data** (strike prices, expiration dates).  
3. Estimates **historical volatility (\u03C3)** using past stock returns.  
4. Computes **call and put option prices** using the Black-Scholes formula.  
5. **Compares results** with real market option prices.  
6. **Visualizes volatility impact** on option prices.  

## **Installation**  
### **1. Install Python & Required Libraries**  
Make sure you have Python installed. Then, install dependencies:  
```sh
pip install yfinance numpy scipy matplotlib
```

### **2. Run the Script**  
Clone the repository and navigate into the project folder:  
```sh
git clone https://github.com/yourusername/Black-Scholes-Pricing.git
cd Black-Scholes-Pricing
python3 black_scholes.py
```

## **Example Output**  
```
Stock Price (S0): $152.34
Strike Price (K): $150.00
Time to Expiry (T): 0.25 years
Risk-Free Rate (r): 0.04
Estimated Volatility (\u03C3): 0.2563

Black-Scholes Call Option Price: $6.78
Black-Scholes Put Option Price: $3.12

Market Call Option Price: $7.00
Market Put Option Price: $3.05
```

## **Visualizing the Impact of Volatility**  
The script also generates a **volatility sensitivity chart** showing how option prices change as volatility increases.


## **Future Improvements**  
- ✅ Add **Greeks Calculation** (Delta, Gamma, Theta, Vega)  
- ✅ Implement **Monte Carlo Simulation** for more accurate option pricing  
- ✅ Compare **Black-Scholes vs. Binomial Tree Model**  

## **Why This Matters**  
This project is useful for **traders, investors, and financial analysts** looking to understand **options pricing and market efficiency**. It can be extended for **quantitative trading strategies**.

---

## **Contact & Contributions**  
If you find this project useful, feel free to **fork it, star it, or contribute!**  

🔗 **GitHub:** [astew24](https://github.com/astew24)  
📧 **Email:** adstewart@ucsd.edu 



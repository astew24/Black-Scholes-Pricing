"""Streamlit web interface for Black-Scholes option pricing calculator."""

import streamlit as st
import pandas as pd
from datetime import datetime
from ..core.pricing import black_scholes, calculate_greeks
from ..utils.market_data import (
    get_stock_data,
    get_option_chain,
    get_risk_free_rate,
    calculate_time_to_expiry
)

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Black-Scholes Option Pricing Calculator",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("Black-Scholes Option Pricing Calculator")
    
    # Sidebar for input parameters
    st.sidebar.header("Input Parameters")
    
    # Ticker input
    ticker = st.sidebar.text_input("Stock Ticker", "AAPL").upper()
    
    try:
        # Get market data
        spot_price, hist_volatility = get_stock_data(ticker)
        risk_free_rate = get_risk_free_rate()
        
        # Get option chain
        option_chain = get_option_chain(ticker)
        expiry_dates = option_chain["calls"].index.get_level_values("expiration").unique()
        
        # Expiry date selection
        expiry_date = st.sidebar.selectbox(
            "Expiration Date",
            options=expiry_dates,
            format_func=lambda x: datetime.strptime(x, "%Y-%m-%d").strftime("%B %d, %Y")
        )
        
        # Get strikes for selected expiry
        strikes = option_chain["calls"].loc[expiry_date]["strike"].values
        
        # Strike price selection
        strike_price = st.sidebar.selectbox(
            "Strike Price",
            options=strikes,
            index=len(strikes) // 2  # Default to middle strike
        )
        
        # Time to expiry
        time_to_expiry = calculate_time_to_expiry(expiry_date)
        
        # Volatility input
        volatility = st.sidebar.number_input(
            "Volatility",
            min_value=0.01,
            max_value=2.0,
            value=float(hist_volatility),
            step=0.01,
            format="%.2f"
        )
        
        # Risk-free rate input
        risk_free_rate = st.sidebar.number_input(
            "Risk-Free Rate",
            min_value=0.0,
            max_value=0.2,
            value=float(risk_free_rate),
            step=0.001,
            format="%.3f"
        )
        
        # Calculate option prices
        call_price = black_scholes(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=volatility,
            option_type="call"
        )
        
        put_price = black_scholes(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=volatility,
            option_type="put"
        )
        
        # Calculate Greeks
        call_greeks = calculate_greeks(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=volatility,
            option_type="call"
        )
        
        put_greeks = calculate_greeks(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=volatility,
            option_type="put"
        )
        
        # Display results in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Market Data")
            st.write(f"Underlying: {ticker}")
            st.write(f"Spot Price: ${spot_price:.2f}")
            st.write(f"Strike Price: ${strike_price:.2f}")
            st.write(f"Time to Expiry: {time_to_expiry:.3f} years")
            st.write(f"Risk-Free Rate: {risk_free_rate:.2%}")
            st.write(f"Volatility: {volatility:.2%}")
        
        with col2:
            st.subheader("Option Prices")
            st.write(f"Call: ${call_price:.2f}")
            st.write(f"Put: ${put_price:.2f}")
        
        # Display Greeks
        st.subheader("Option Greeks")
        
        # Create DataFrame for Greeks
        greeks_data = {
            "Call": call_greeks,
            "Put": put_greeks
        }
        greeks_df = pd.DataFrame(greeks_data)
        st.dataframe(greeks_df.style.format("{:.4f}"))
        
        # Sensitivity Analysis
        st.subheader("Sensitivity Analysis")
        
        # Parameter selection for sensitivity analysis
        param = st.selectbox(
            "Parameter to Analyze",
            options=["volatility", "time", "spot", "strike"]
        )
        
        # Generate sensitivity plot
        from ..visualization.plots import plot_price_sensitivity
        plot_price_sensitivity(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=volatility,
            parameter=param
        )
        
        # Greeks sensitivity
        st.subheader("Greeks Sensitivity")
        greek_param = st.selectbox(
            "Parameter to Analyze",
            options=["spot", "time", "volatility"]
        )
        
        from ..visualization.plots import plot_greeks
        plot_greeks(
            spot_price=spot_price,
            strike_price=strike_price,
            time_to_expiry=time_to_expiry,
            risk_free_rate=risk_free_rate,
            volatility=volatility,
            parameter=greek_param
        )
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 
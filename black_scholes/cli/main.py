"""Command-line interface for Black-Scholes option pricing calculator."""

import argparse
from datetime import datetime
from typing import Optional
from ..core.pricing import black_scholes, calculate_greeks
from ..utils.market_data import (
    get_stock_data,
    get_option_chain,
    get_risk_free_rate,
    calculate_time_to_expiry
)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Black-Scholes Option Pricing Calculator"
    )
    
    # Required arguments
    parser.add_argument(
        "ticker",
        type=str,
        help="Stock ticker symbol (e.g., AAPL)"
    )
    
    # Optional arguments
    parser.add_argument(
        "--strike",
        type=float,
        help="Strike price (if not provided, will use ATM strike)"
    )
    parser.add_argument(
        "--expiry",
        type=str,
        help="Expiration date (YYYY-MM-DD, if not provided, will use nearest expiry)"
    )
    parser.add_argument(
        "--volatility",
        type=float,
        help="Volatility (if not provided, will calculate from historical data)"
    )
    parser.add_argument(
        "--risk-free-rate",
        type=float,
        help="Risk-free rate (if not provided, will use current Treasury yield)"
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Generate sensitivity plots"
    )
    
    return parser.parse_args()

def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()
    
    try:
        # Get market data
        spot_price, hist_volatility = get_stock_data(args.ticker)
        risk_free_rate = args.risk_free_rate or get_risk_free_rate()
        
        # Get option chain
        option_chain = get_option_chain(args.ticker, args.expiry)
        expiry_date = option_chain["expiry"]
        time_to_expiry = calculate_time_to_expiry(expiry_date)
        
        # Determine strike price
        if args.strike is None:
            # Use ATM strike (closest to spot price)
            strikes = option_chain["calls"]["strike"].values
            strike_price = min(strikes, key=lambda x: abs(x - spot_price))
        else:
            strike_price = args.strike
        
        # Use provided volatility or historical volatility
        volatility = args.volatility or hist_volatility
        
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
        
        # Print results
        print("\nBlack-Scholes Option Pricing Results")
        print("===================================")
        print(f"Underlying: {args.ticker}")
        print(f"Spot Price: ${spot_price:.2f}")
        print(f"Strike Price: ${strike_price:.2f}")
        print(f"Time to Expiry: {time_to_expiry:.3f} years")
        print(f"Risk-Free Rate: {risk_free_rate:.2%}")
        print(f"Volatility: {volatility:.2%}")
        print("\nOption Prices:")
        print(f"Call: ${call_price:.2f}")
        print(f"Put: ${put_price:.2f}")
        
        print("\nCall Option Greeks:")
        for greek, value in call_greeks.items():
            print(f"{greek.capitalize()}: {value:.4f}")
        
        print("\nPut Option Greeks:")
        for greek, value in put_greeks.items():
            print(f"{greek.capitalize()}: {value:.4f}")
        
        # Generate plots if requested
        if args.plot:
            from ..visualization.plots import plot_price_sensitivity, plot_greeks
            
            print("\nGenerating sensitivity plots...")
            plot_price_sensitivity(
                spot_price=spot_price,
                strike_price=strike_price,
                time_to_expiry=time_to_expiry,
                risk_free_rate=risk_free_rate,
                volatility=volatility
            )
            
            plot_greeks(
                spot_price=spot_price,
                strike_price=strike_price,
                time_to_expiry=time_to_expiry,
                risk_free_rate=risk_free_rate,
                volatility=volatility
            )
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
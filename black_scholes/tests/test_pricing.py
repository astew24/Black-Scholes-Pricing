"""Unit tests for Black-Scholes option pricing."""

import pytest
import numpy as np
from ..core.pricing import black_scholes, calculate_greeks

def test_black_scholes_call():
    """Test Black-Scholes call option pricing."""
    # Test case 1: ATM call option
    price = black_scholes(
        spot_price=100,
        strike_price=100,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        option_type="call"
    )
    assert price > 0
    assert abs(price - 10.45) < 0.1  # Approximate value
    
    # Test case 2: ITM call option
    price = black_scholes(
        spot_price=110,
        strike_price=100,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        option_type="call"
    )
    assert price > 0
    assert price > 10  # Should be more valuable than ATM option
    
    # Test case 3: OTM call option
    price = black_scholes(
        spot_price=90,
        strike_price=100,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        option_type="call"
    )
    assert price > 0
    assert price < 10  # Should be less valuable than ATM option

def test_black_scholes_put():
    """Test Black-Scholes put option pricing."""
    # Test case 1: ATM put option
    price = black_scholes(
        spot_price=100,
        strike_price=100,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        option_type="put"
    )
    assert price > 0
    assert abs(price - 5.57) < 0.1  # Approximate value
    
    # Test case 2: ITM put option
    price = black_scholes(
        spot_price=90,
        strike_price=100,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        option_type="put"
    )
    assert price > 0
    assert price > 5  # Should be more valuable than ATM option
    
    # Test case 3: OTM put option
    price = black_scholes(
        spot_price=110,
        strike_price=100,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        option_type="put"
    )
    assert price > 0
    assert price < 5  # Should be less valuable than ATM option

def test_black_scholes_input_validation():
    """Test input validation for Black-Scholes pricing."""
    # Test invalid spot price
    with pytest.raises(ValueError):
        black_scholes(
            spot_price=-100,
            strike_price=100,
            time_to_expiry=1.0,
            risk_free_rate=0.05,
            volatility=0.2,
            option_type="call"
        )
    
    # Test invalid strike price
    with pytest.raises(ValueError):
        black_scholes(
            spot_price=100,
            strike_price=-100,
            time_to_expiry=1.0,
            risk_free_rate=0.05,
            volatility=0.2,
            option_type="call"
        )
    
    # Test invalid time to expiry
    with pytest.raises(ValueError):
        black_scholes(
            spot_price=100,
            strike_price=100,
            time_to_expiry=-1.0,
            risk_free_rate=0.05,
            volatility=0.2,
            option_type="call"
        )
    
    # Test invalid volatility
    with pytest.raises(ValueError):
        black_scholes(
            spot_price=100,
            strike_price=100,
            time_to_expiry=1.0,
            risk_free_rate=0.05,
            volatility=-0.2,
            option_type="call"
        )
    
    # Test invalid option type
    with pytest.raises(ValueError):
        black_scholes(
            spot_price=100,
            strike_price=100,
            time_to_expiry=1.0,
            risk_free_rate=0.05,
            volatility=0.2,
            option_type="invalid"
        )

def test_greeks_calculation():
    """Test calculation of option Greeks."""
    # Test call option Greeks
    greeks = calculate_greeks(
        spot_price=100,
        strike_price=100,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        option_type="call"
    )
    
    assert "delta" in greeks
    assert "gamma" in greeks
    assert "theta" in greeks
    assert "vega" in greeks
    assert "rho" in greeks
    
    # Test put option Greeks
    greeks = calculate_greeks(
        spot_price=100,
        strike_price=100,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        option_type="put"
    )
    
    assert "delta" in greeks
    assert "gamma" in greeks
    assert "theta" in greeks
    assert "vega" in greeks
    assert "rho" in greeks
    
    # Verify put-call parity for delta
    call_greeks = calculate_greeks(
        spot_price=100,
        strike_price=100,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        option_type="call"
    )
    
    put_greeks = calculate_greeks(
        spot_price=100,
        strike_price=100,
        time_to_expiry=1.0,
        risk_free_rate=0.05,
        volatility=0.2,
        option_type="put"
    )
    
    assert abs(call_greeks["delta"] + put_greeks["delta"] - 1) < 1e-10
    assert abs(call_greeks["gamma"] - put_greeks["gamma"]) < 1e-10
    assert abs(call_greeks["vega"] - put_greeks["vega"]) < 1e-10 
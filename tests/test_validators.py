"""
tests/test_validators.py

Unit tests for input validators using pytest.
"""

import pytest
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
    validate_order_inputs,
)


def test_validate_symbol_valid():
    """Test valid symbol strings."""
    assert validate_symbol("BTCUSDT") == "BTCUSDT"
    assert validate_symbol("ethusdt") == "ETHUSDT"
    assert validate_symbol(" SOLUSDT ") == "SOLUSDT"


def test_validate_symbol_invalid():
    """Test invalid symbol strings."""
    with pytest.raises(ValueError):
        validate_symbol("")
    with pytest.raises(ValueError):
        validate_symbol("BTC-USDT")
    with pytest.raises(ValueError):
        validate_symbol("BTC USDT")
    with pytest.raises(ValueError):
        validate_symbol("A")  # too short


def test_validate_side_valid():
    """Test valid order sides."""
    assert validate_side("BUY") == "BUY"
    assert validate_side("sell") == "SELL"


def test_validate_side_invalid():
    """Test invalid order sides."""
    with pytest.raises(ValueError):
        validate_side("")
    with pytest.raises(ValueError):
        validate_side("HOLD")


def test_validate_order_type_valid():
    """Test valid order types."""
    assert validate_order_type("MARKET") == "MARKET"
    assert validate_order_type("limit") == "LIMIT"
    assert validate_order_type("STOP_LIMIT") == "STOP_LIMIT"


def test_validate_order_type_invalid():
    """Test invalid order types."""
    with pytest.raises(ValueError):
        validate_order_type("")
    with pytest.raises(ValueError):
        validate_order_type("STOP_LOSS")


def test_validate_quantity_valid():
    """Test valid quantities."""
    assert validate_quantity("0.001") == 0.001
    assert validate_quantity("10") == 10.0


def test_validate_quantity_invalid():
    """Test invalid quantities."""
    with pytest.raises(ValueError):
        validate_quantity("")
    with pytest.raises(ValueError):
        validate_quantity("-0.5")
    with pytest.raises(ValueError):
        validate_quantity("0")
    with pytest.raises(ValueError):
        validate_quantity("abc")


def test_validate_price_market():
    """Test price validation for MARKET orders (price ignored/None)."""
    assert validate_price(None, "MARKET") is None
    assert validate_price("100", "MARKET") is None


def test_validate_price_limit_valid():
    """Test valid price inputs for LIMIT orders."""
    assert validate_price("28000.50", "LIMIT") == 28000.50
    assert validate_price("28000.50", "STOP_LIMIT") == 28000.50


def test_validate_price_limit_invalid():
    """Test invalid price inputs for LIMIT/STOP_LIMIT orders."""
    with pytest.raises(ValueError):
        validate_price(None, "LIMIT")
    with pytest.raises(ValueError):
        validate_price("-100", "LIMIT")
    with pytest.raises(ValueError):
        validate_price(None, "STOP_LIMIT")


def test_validate_stop_price_valid():
    """Test valid stop-price inputs."""
    assert validate_stop_price("27900.00", "STOP_LIMIT") == 27900.00
    assert validate_stop_price(None, "LIMIT") is None
    assert validate_stop_price("100", "MARKET") is None


def test_validate_stop_price_invalid():
    """Test invalid stop-price inputs for STOP_LIMIT."""
    with pytest.raises(ValueError):
        validate_stop_price(None, "STOP_LIMIT")
    with pytest.raises(ValueError):
        validate_stop_price("-50", "STOP_LIMIT")
    with pytest.raises(ValueError):
        validate_stop_price("abc", "STOP_LIMIT")


def test_validate_order_inputs_valid():
    """Test master validator with valid inputs."""
    # Market Order
    res_market = validate_order_inputs("btcusdt", "buy", "market", "0.005")
    assert res_market == {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "order_type": "MARKET",
        "quantity": 0.005,
        "price": None,
        "stop_price": None,
    }

    # Limit Order
    res_limit = validate_order_inputs("btcusdt", "buy", "limit", "0.005", "27500.50")
    assert res_limit == {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "quantity": 0.005,
        "price": 27500.50,
        "stop_price": None,
    }

    # Stop-Limit Order
    res_stop_limit = validate_order_inputs("btcusdt", "sell", "stop_limit", "0.005", "27500.50", "27600.00")
    assert res_stop_limit == {
        "symbol": "BTCUSDT",
        "side": "SELL",
        "order_type": "STOP_LIMIT",
        "quantity": 0.005,
        "price": 27500.50,
        "stop_price": 27600.00,
    }


def test_validate_order_inputs_invalid():
    """Test master validator throws ValueError on the first invalid field."""
    # Missing price for LIMIT
    with pytest.raises(ValueError):
        validate_order_inputs("BTCUSDT", "BUY", "LIMIT", "0.005", None)
    # Missing stop_price for STOP_LIMIT
    with pytest.raises(ValueError):
        validate_order_inputs("BTCUSDT", "BUY", "STOP_LIMIT", "0.005", "27000.00", None)

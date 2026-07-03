"""
tests/test_client.py

Unit tests for the Binance Testnet Client wrapper using pytest and unittest.mock.
"""

from unittest.mock import MagicMock, patch
import pytest
from binance.exceptions import BinanceAPIException
from bot.client import BinanceTestnetClient


@pytest.fixture
def mock_binance_client():
    """Fixture to mock the python-binance Client dependency."""
    with patch("bot.client.Client") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        yield mock_instance


def test_client_init(mock_binance_client):
    """Test client initialization loads environment correctly."""
    client = BinanceTestnetClient("fake_key", "fake_secret")
    assert client is not None


def test_client_init_error():
    """Test client raises ValueError if keys are empty."""
    with pytest.raises(ValueError):
        BinanceTestnetClient("", "")


def test_place_market_order_success(mock_binance_client):
    """Test successfully placing a MARKET order."""
    client = BinanceTestnetClient("fake_key", "fake_secret")

    # Mock response
    mock_binance_client.futures_create_order.return_value = {
        "orderId": 123456,
        "status": "FILLED",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "executedQty": "0.001",
        "avgPrice": "27000.00",
    }

    response = client.place_order("BTCUSDT", "BUY", "MARKET", 0.001)

    assert response["orderId"] == 123456
    assert response["status"] == "FILLED"
    mock_binance_client.futures_create_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="BUY",
        type="MARKET",
        quantity=0.001,
    )


def test_place_limit_order_success(mock_binance_client):
    """Test successfully placing a LIMIT order."""
    client = BinanceTestnetClient("fake_key", "fake_secret")

    # Mock response
    mock_binance_client.futures_create_order.return_value = {
        "orderId": 654321,
        "status": "NEW",
        "symbol": "BTCUSDT",
        "side": "SELL",
        "type": "LIMIT",
        "executedQty": "0.000",
        "avgPrice": "0.00",
    }

    response = client.place_order("BTCUSDT", "SELL", "LIMIT", 0.002, 28000.0)

    assert response["orderId"] == 654321
    assert response["status"] == "NEW"
    mock_binance_client.futures_create_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="SELL",
        type="LIMIT",
        quantity=0.002,
        price=28000.0,
        timeInForce="GTC",
    )


def test_place_stop_limit_order_success(mock_binance_client):
    """Test successfully placing a STOP_LIMIT order."""
    client = BinanceTestnetClient("fake_key", "fake_secret")

    # Mock response
    mock_binance_client.futures_create_order.return_value = {
        "orderId": 987654,
        "status": "NEW",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "STOP",
        "executedQty": "0.000",
        "avgPrice": "0.00",
    }

    response = client.place_order("BTCUSDT", "BUY", "STOP_LIMIT", 0.003, 28000.0, 27900.0)

    assert response["orderId"] == 987654
    assert response["status"] == "NEW"
    mock_binance_client.futures_create_order.assert_called_once_with(
        symbol="BTCUSDT",
        side="BUY",
        type="STOP",
        quantity=0.003,
        price=28000.0,
        stopPrice=27900.0,
        timeInForce="GTC",
    )


def test_place_order_api_exception(mock_binance_client):
    """Test Binance API error handling."""
    client = BinanceTestnetClient("fake_key", "fake_secret")

    # Mock BinanceAPIException
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = '{"code": -2019, "msg": "Margin is insufficient."}'
    mock_binance_client.futures_create_order.side_effect = BinanceAPIException(
        response=mock_response,
        status_code=400,
        text='{"code": -2019, "msg": "Margin is insufficient."}',
    )

    with pytest.raises(BinanceAPIException) as exc_info:
        client.place_order("BTCUSDT", "BUY", "MARKET", 10.0)

    assert exc_info.value.code == -2019
    assert "Margin is insufficient" in exc_info.value.message

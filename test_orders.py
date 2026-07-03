"""
Quick test for bot/orders.py — mocks client to verify order delegation works.
"""

from unittest.mock import MagicMock
from bot.orders import execute_order
from bot.client import BinanceTestnetClient

# Create a mock client
mock_client = MagicMock(spec=BinanceTestnetClient)
mock_client.place_order.return_value = {
    "orderId": 11223344,
    "status": "NEW",
    "executedQty": "0.000",
    "avgPrice": "0.00",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "LIMIT"
}

print("Running execute_order dry run with mock client...")

# Test executing a limit order
response = execute_order(
    client=mock_client,
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT",
    quantity=0.005,
    price=27500.0
)

# Assertions
mock_client.place_order.assert_called_once_with(
    symbol="BTCUSDT",
    side="BUY",
    order_type="LIMIT",
    quantity=0.005,
    price=27500.0
)

print("✅ execute_order mock test passed!")
print(f"Response: {response}")

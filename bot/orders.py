"""
bot/orders.py

Exposes high-level order execution functions. Connects the validated inputs
to the Binance API Client.
"""

from typing import Optional
from bot.client import BinanceTestnetClient


def execute_order(
    client: BinanceTestnetClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> dict:
    """
    Delegates validated order placement parameters to the Binance client.

    Args:
        client:     The initialized BinanceTestnetClient.
        symbol:     Trading pair (e.g. 'BTCUSDT').
        side:       Order side ('BUY' or 'SELL').
        order_type: Order type ('MARKET', 'LIMIT', or 'STOP_LIMIT').
        quantity:   Quantity to trade (positive float).
        price:      Price for LIMIT/STOP_LIMIT orders (positive float, or None for MARKET).
        stop_price: Trigger price for STOP_LIMIT orders (positive float, or None for MARKET/LIMIT).

    Returns:
        A dictionary containing the API response details.
    """
    # Simply delegates the order placement to the API Client layer
    response = client.place_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
    )
    return response

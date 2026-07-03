"""
bot/client.py

Wraps the python-binance client specifically for Binance Futures Testnet (USDT-M)
and handles logging, authentication, and exception mapping.
"""

import os
from typing import Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from bot.logging_config import setup_logger, log_request, log_response, log_exception

# Initialize logger for the client module
logger = setup_logger()


class BinanceTestnetClient:
    """
    Wrapper for the Binance API Client configured for the Futures Testnet.
    """

    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize the Binance Client.

        Args:
            api_key: The Binance Testnet API key.
            api_secret: The Binance Testnet API secret.
        """
        if not api_key or not api_secret:
            raise ValueError("API Key and Secret must be provided to initialize the client.")

        # Initialize the python-binance client with testnet=True
        # This automatically routes Futures calls to https://testnet.binancefuture.com
        self.client = Client(api_key, api_secret, testnet=True)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
    ) -> dict:
        """
        Place a Market, Limit, or Stop-Limit order on Binance Futures Testnet (USDT-M).

        Args:
            symbol:     Trading pair (e.g., 'BTCUSDT').
            side:       Order side ('BUY' or 'SELL').
            order_type: Order type ('MARKET', 'LIMIT', or 'STOP_LIMIT').
            quantity:   Quantity to trade.
            price:      Price for LIMIT and STOP_LIMIT orders (ignored for MARKET).
            stop_price: Trigger price for STOP_LIMIT orders (ignored for MARKET/LIMIT).

        Returns:
            The raw response dictionary from the Binance API.

        Raises:
            BinanceAPIException: If the Binance API returns an error.
            Exception:           For network or other runtime failures.
        """
        # Map internal STOP_LIMIT to Binance Futures API order type "STOP"
        api_type = "STOP" if order_type == "STOP_LIMIT" else order_type

        # Prepare parameters for the API request
        params = {
            "symbol": symbol,
            "side": side,
            "type": api_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = "GTC"  # Good 'Til Cancelled is standard for limit orders
        elif order_type == "STOP_LIMIT":
            params["price"] = price
            params["stopPrice"] = stop_price
            params["timeInForce"] = "GTC"  # Good 'Til Cancelled is standard for stop-limit orders

        # Log the outgoing request before calling the API
        log_request(logger, "/fapi/v1/order", params)

        try:
            # Place order on Futures USDT-M Testnet
            response = self.client.futures_create_order(**params)

            # Log the response on success
            log_response(logger, response)
            return response

        except (BinanceAPIException, BinanceOrderException) as e:
            # Log specific Binance API exception
            log_exception(logger, e, context=f"Binance order failure (Type: {type(e).__name__})")
            raise
        except Exception as e:
            # Log generic connection/network exception
            log_exception(logger, e, context="Network or unexpected error while placing order")
            raise

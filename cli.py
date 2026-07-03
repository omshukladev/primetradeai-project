"""
cli.py

The main command-line interface entry point for the Binance Futures Testnet Trading Bot.
Parses arguments, validates inputs, executes orders, logs events, and prints colored output.
"""

import os
import sys
import argparse
from typing import Optional
from dotenv import load_dotenv
from colorama import init, Fore, Style

from bot.validators import validate_order_inputs
from bot.client import BinanceTestnetClient
from bot.orders import execute_order
from bot.logging_config import setup_logger, log_validation_error, log_exception

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# Initialize logger
logger = setup_logger()


def print_request_summary(symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None) -> None:
    """Print a clean summary of the order request before sending it."""
    print(f"\n{Fore.CYAN}═══════════════════════════════════════")
    print(f"{Fore.CYAN}   Binance Futures Testnet Bot")
    print(f"{Fore.CYAN}═══════════════════════════════════════")
    print(f"{Fore.GREEN}[INFO] Placing {order_type} {side} order...")
    print(f"  Symbol   : {symbol}")
    print(f"  Quantity : {quantity}")
    if order_type == "LIMIT" and price is not None:
        print(f"  Price    : {price}")
    print()


def print_response_summary(response: dict) -> None:
    """Print the formatted response details from the Binance order execution."""
    print(f"{Fore.GREEN}[INFO] Order placed successfully!")
    print(f"  Order ID     : {response.get('orderId')}")
    print(f"  Status       : {response.get('status')}")
    print(f"  Executed Qty : {response.get('executedQty')}")
    
    # Try to extract average price
    avg_price = response.get("avgPrice")
    if not avg_price or float(avg_price) == 0:
        # Fallback fields for average price or fill price
        avg_price = response.get("price", "N/A")
    print(f"  Avg Price    : {avg_price}")
    print(f"{Fore.CYAN}═══════════════════════════════════════\n")


def main() -> None:
    """Main CLI execution flow."""
    # Setup argparse
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot CLI."
    )
    parser.add_argument(
        "-s", "--symbol", required=True, help="Trading pair symbol (e.g. BTCUSDT)"
    )
    parser.add_argument(
        "-d", "--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side (BUY/SELL)"
    )
    parser.add_argument(
        "-t", "--type", required=True, choices=["MARKET", "LIMIT", "market", "limit"], help="Order type (MARKET/LIMIT)"
    )
    parser.add_argument(
        "-q", "--quantity", required=True, help="Quantity to trade (positive number)"
    )
    parser.add_argument(
        "-p", "--price", help="Price (required for LIMIT orders)"
    )

    # Parse arguments
    args = parser.parse_args()

    # 1. Validate Input
    try:
        validated_inputs = validate_order_inputs(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValueError as val_err:
        # Log validation error
        log_validation_error(logger, "CLI Input", str(args.__dict__), str(val_err))
        # Print error in red and exit
        print(f"{Fore.RED}[ERROR] Validation failed: {val_err}", file=sys.stderr)
        sys.exit(1)

    # 2. Load API credentials
    load_dotenv()
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        exc = ValueError("API keys are missing in your .env file.")
        log_exception(logger, exc, "Loading .env keys in cli.py")
        print(
            f"{Fore.RED}[ERROR] Configuration error: BINANCE_API_KEY and BINANCE_API_SECRET must be set in your .env file.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 3. Print Request Summary
    print_request_summary(
        symbol=validated_inputs["symbol"],
        side=validated_inputs["side"],
        order_type=validated_inputs["order_type"],
        quantity=validated_inputs["quantity"],
        price=validated_inputs["price"],
    )

    # 4. Instantiate API Client & Execute Order
    try:
        client = BinanceTestnetClient(api_key, api_secret)
        response = execute_order(
            client=client,
            symbol=validated_inputs["symbol"],
            side=validated_inputs["side"],
            order_type=validated_inputs["order_type"],
            quantity=validated_inputs["quantity"],
            price=validated_inputs["price"],
        )
        
        # 5. Print Response Details
        print_response_summary(response)

    except Exception as exc:
        # Exceptions are already logged inside bot/client.py
        # Here we just output the error details to the console user-friendly
        print(f"{Fore.RED}[ERROR] Order execution failed:")
        print(f"  {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

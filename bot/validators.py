"""
bot/validators.py

Validates all user input from the CLI before any API call is made.

Rules:
    symbol   → non-empty string, alphanumeric only, 2-20 chars
    side     → must be BUY or SELL (case-insensitive)
    order_type → must be MARKET or LIMIT (case-insensitive)
    quantity → must be a positive float
    price    → required for LIMIT orders, must be a positive float
"""

from typing import Optional


# ── Constants ─────────────────────────────────────────────────────────────────

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


# ── Individual validators ─────────────────────────────────────────────────────

def validate_symbol(symbol: str) -> str:
    """
    Validate the trading pair symbol.

    Rules:
        - Must be a non-empty string
        - Must contain only alphanumeric characters (no spaces or special chars)
        - Length between 2 and 20 characters

    Args:
        symbol: The trading pair string (e.g. 'BTCUSDT').

    Returns:
        The symbol in uppercase.

    Raises:
        ValueError: If any rule is violated.
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError("--symbol is required and must be a non-empty string.")

    symbol = symbol.strip().upper()

    if not symbol.isalnum():
        raise ValueError(
            f"--symbol '{symbol}' is invalid. Only letters and numbers are allowed (e.g. BTCUSDT)."
        )

    if not (2 <= len(symbol) <= 20):
        raise ValueError(
            f"--symbol '{symbol}' is invalid. Length must be between 2 and 20 characters."
        )

    return symbol


def validate_side(side: str) -> str:
    """
    Validate the order side.

    Rules:
        - Must be 'BUY' or 'SELL' (case-insensitive)

    Args:
        side: The order side string.

    Returns:
        The side in uppercase ('BUY' or 'SELL').

    Raises:
        ValueError: If the value is not a valid side.
    """
    if not side or not isinstance(side, str):
        raise ValueError("--side is required.")

    side = side.strip().upper()

    if side not in VALID_SIDES:
        raise ValueError(
            f"--side '{side}' is invalid. Must be one of: {', '.join(sorted(VALID_SIDES))}."
        )

    return side


def validate_order_type(order_type: str) -> str:
    """
    Validate the order type.

    Rules:
        - Must be 'MARKET' or 'LIMIT' (case-insensitive)

    Args:
        order_type: The order type string.

    Returns:
        The order type in uppercase ('MARKET' or 'LIMIT').

    Raises:
        ValueError: If the value is not a valid order type.
    """
    if not order_type or not isinstance(order_type, str):
        raise ValueError("--type is required.")

    order_type = order_type.strip().upper()

    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"--type '{order_type}' is invalid. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )

    return order_type


def validate_quantity(quantity: str) -> float:
    """
    Validate the order quantity.

    Rules:
        - Must be convertible to a float
        - Must be greater than 0

    Args:
        quantity: The quantity string from CLI input.

    Returns:
        The quantity as a positive float.

    Raises:
        ValueError: If the value is not a valid positive number.
    """
    if quantity is None:
        raise ValueError("--quantity is required.")

    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(
            f"--quantity '{quantity}' is invalid. Must be a positive number (e.g. 0.001)."
        )

    if qty <= 0:
        raise ValueError(
            f"--quantity '{quantity}' is invalid. Must be greater than 0."
        )

    return qty


def validate_price(price: Optional[str], order_type: str) -> Optional[float]:
    """
    Validate the order price.

    Rules:
        - Required if order_type is 'LIMIT'
        - Must be convertible to a float
        - Must be greater than 0
        - Optional (None is acceptable) for MARKET orders

    Args:
        price:      The price string from CLI input, or None.
        order_type: The validated order type ('MARKET' or 'LIMIT').

    Returns:
        The price as a positive float, or None for MARKET orders.

    Raises:
        ValueError: If price is missing for LIMIT or is an invalid number.
    """
    if order_type == "LIMIT":
        if price is None:
            raise ValueError(
                "--price is required for LIMIT orders. "
                "Example: --price 28000.00"
            )

        try:
            p = float(price)
        except (ValueError, TypeError):
            raise ValueError(
                f"--price '{price}' is invalid. Must be a positive number (e.g. 28000.00)."
            )

        if p <= 0:
            raise ValueError(
                f"--price '{price}' is invalid. Must be greater than 0."
            )

        return p

    # MARKET order — price is ignored
    return None


# ── Master validator ──────────────────────────────────────────────────────────

def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
) -> dict:
    """
    Run all validations in sequence and return cleaned, typed values.

    Calls each individual validator. The first failure raises a ValueError
    with a clear message — no API call is ever made if validation fails.

    Args:
        symbol:     Trading pair (e.g. 'BTCUSDT').
        side:       Order side ('BUY' or 'SELL').
        order_type: Order type ('MARKET' or 'LIMIT').
        quantity:   Order quantity as string.
        price:      Order price as string, or None for MARKET orders.

    Returns:
        dict with keys: symbol, side, order_type, quantity, price
        All values are cleaned and correctly typed.

    Raises:
        ValueError: On the first validation failure encountered.
    """
    validated_symbol     = validate_symbol(symbol)
    validated_side       = validate_side(side)
    validated_order_type = validate_order_type(order_type)
    validated_quantity   = validate_quantity(quantity)
    validated_price      = validate_price(price, validated_order_type)

    return {
        "symbol":     validated_symbol,
        "side":       validated_side,
        "order_type": validated_order_type,
        "quantity":   validated_quantity,
        "price":      validated_price,
    }

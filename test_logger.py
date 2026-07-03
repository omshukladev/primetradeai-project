"""Quick test for bot/logging_config.py — run this to verify the logger works."""

from bot.logging_config import (
    setup_logger,
    log_request,
    log_response,
    log_validation_error,
    log_exception,
)

logger = setup_logger()

log_request(logger, "/fapi/v1/order", {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "quantity": 0.001,
})

log_response(logger, {
    "orderId": 99999,
    "status": "FILLED",
    "executedQty": "0.001",
    "avgPrice": "27000.00",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
})

log_validation_error(logger, "--price", None, "price is required for LIMIT orders")

log_exception(logger, ValueError("bad quantity"), "test run")

print("✅ Logger test passed!")
print("📄 Check: logs/trading_bot.log")

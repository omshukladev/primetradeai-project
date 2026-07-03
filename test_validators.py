"""Quick test for bot/validators.py — run this to verify all validations work."""

from bot.validators import validate_order_inputs

passed = 0
failed = 0


def check(label: str, fn, expect_error: bool = False):
    """Helper to run a test case and print pass/fail."""
    global passed, failed
    try:
        result = fn()
        if expect_error:
            print(f"  ❌ FAIL  {label} — expected error but got: {result}")
            failed += 1
        else:
            print(f"  ✅ PASS  {label} → {result}")
            passed += 1
    except ValueError as e:
        if expect_error:
            print(f"  ✅ PASS  {label} → caught: {e}")
            passed += 1
        else:
            print(f"  ❌ FAIL  {label} — unexpected error: {e}")
            failed += 1


print("\n── Valid inputs ─────────────────────────────────────────────────")

check("MARKET BUY",  lambda: validate_order_inputs("BTCUSDT", "BUY",  "MARKET", "0.001"))
check("MARKET SELL", lambda: validate_order_inputs("ETHUSDT", "SELL", "MARKET", "0.5"))
check("LIMIT BUY",   lambda: validate_order_inputs("BTCUSDT", "BUY",  "LIMIT",  "0.001", "28000"))
check("LIMIT SELL",  lambda: validate_order_inputs("BTCUSDT", "SELL", "LIMIT",  "0.002", "30000.50"))
check("lowercase inputs", lambda: validate_order_inputs("btcusdt", "buy", "market", "0.001"))

print("\n── Invalid inputs (should all fail) ────────────────────────────")

check("empty symbol",         lambda: validate_order_inputs("",        "BUY",  "MARKET", "0.001"),        expect_error=True)
check("symbol with spaces",   lambda: validate_order_inputs("BTC USDT","BUY",  "MARKET", "0.001"),        expect_error=True)
check("bad side",             lambda: validate_order_inputs("BTCUSDT", "HOLD", "MARKET", "0.001"),        expect_error=True)
check("bad order type",       lambda: validate_order_inputs("BTCUSDT", "BUY",  "STOP",   "0.001"),        expect_error=True)
check("zero quantity",        lambda: validate_order_inputs("BTCUSDT", "BUY",  "MARKET", "0"),            expect_error=True)
check("negative quantity",    lambda: validate_order_inputs("BTCUSDT", "BUY",  "MARKET", "-1"),           expect_error=True)
check("text quantity",        lambda: validate_order_inputs("BTCUSDT", "BUY",  "MARKET", "abc"),          expect_error=True)
check("LIMIT without price",  lambda: validate_order_inputs("BTCUSDT", "BUY",  "LIMIT",  "0.001"),        expect_error=True)
check("LIMIT price = 0",      lambda: validate_order_inputs("BTCUSDT", "BUY",  "LIMIT",  "0.001", "0"),   expect_error=True)
check("LIMIT negative price", lambda: validate_order_inputs("BTCUSDT", "BUY",  "LIMIT",  "0.001", "-100"),expect_error=True)

print(f"\n── Results: {passed} passed / {failed} failed ──────────────────────────\n")

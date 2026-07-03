"""
Quick test for bot/client.py — run this to verify the client initializes and reads .env keys.
"""

import os
from dotenv import load_dotenv
from bot.client import BinanceTestnetClient

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

print("── Key Verification ─────────────────────────────────────────────")
print(f"API Key Found    : {'Yes' if api_key else 'No (Please check .env)'}")
print(f"API Secret Found : {'Yes' if api_secret else 'No (Please check .env)'}")

if not api_key or not api_secret:
    print("\n[ERROR] Missing API credentials in .env. Please fill them out before testing.")
    exit(1)

print("\nInitializing client...")
try:
    client = BinanceTestnetClient(api_key, api_secret)
    print("✅ Client initialized successfully!")
    
    # Simple testnet connection check (ping/server time)
    print("Pinging Binance Futures Testnet...")
    server_time = client.client.futures_time()
    print(f"✅ Connection successful! Server Time: {server_time.get('serverTime')}")
    
except Exception as e:
    print(f"❌ Failed to initialize client or connect: {e}")

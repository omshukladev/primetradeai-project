# Binance Futures Testnet Trading Bot

A high-quality, production-ready Python CLI trading bot designed to place Market, Limit, and Stop-Limit orders on the **Binance Futures Testnet (USDT-M)**.

This project was built for the **Primetrade.ai** Node.js Developer internship assignment.

---

## 🌟 Key Features

* **Order Types**: Full support for `MARKET`, `LIMIT`, and `STOP_LIMIT` (Bonus Feature) order types on both `BUY` and `SELL` sides.
* **Algorithmic Order Support**: Automatically handles Binance's algorithmic order system for Stop-Limit orders (safely maps response fields like `algoId` and `algoStatus`).
* **Input Validation**: Rejects invalid inputs *before* making any API calls (validates symbols, quantity thresholds, order type logic, and conditional parameter combinations).
* **JSON-Line Logging**: Outputs newline-delimited JSON logs to `logs/trading_bot.log` with file rotation (max 5MB, 3 backups) to protect server disk space.
* **Error Handling**: Graceful parsing and colored terminal reporting for network issues, input validation failures, and Binance API errors.
* **Robust Test Suite**: 21 unit tests covering validation constraints and API client wrappers using mock dependencies.

---

## 📂 Project Structure

```text
Primetradeai-project/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance client wrapper
│   ├── orders.py          # order routing logic
│   ├── validators.py      # CLI input validators
│   └── logging_config.py  # rotating JSON logger setup
├── docs/
│   ├── architecture.md    # High-level architecture details
│   ├── checklist.md       # Pre-submission sanity checks
│   ├── phases.md          # 8-phase project roadmap
│   ├── session-log.md     # Engineering session tracking log
│   ├── techstack.md       # Choice of libraries, tools, and versions
│   └── ui-ux.md           # CLI syntax and console design
├── logs/
│   ├── trading_bot.log    # Cumulative runtime logs
│   ├── market_order.log   # Deliverable: Live market order log
│   ├── limit_order.log    # Deliverable: Live limit order log
│   └── stop_limit_order.log # Bonus Deliverable: Live stop-limit order log
├── tests/
│   ├── test_client.py     # API wrapper mock tests
│   └── test_validators.py # Validation unit tests
├── cli.py                 # CLI Command entry point
├── requirements.txt       # Dependencies
├── .env.example           # Template for API Keys
├── .gitignore
├── CLAUDE.md              # AI project guidelines
└── AGENTS.md              # Multi-Agent runtime settings
```

---

## 🚀 Setup & Installation

### Prerequisite
* Python 3.11+

### 1. Install `uv` Package Manager
Due to common macOS system library conflicts (`pyexpat`/`ensurepip` bugs), we recommend using **`uv`** to build the virtual environment:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Scaffold Virtual Environment & Install Dependencies
Create the environment and install dependencies in one command:
```bash
# Create venv using Python 3.13 (or your local python3)
uv venv venv --python 3.13

# Install dependencies from requirements.txt
uv pip install -r requirements.txt --python venv/bin/python
```

### 3. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 4. Configure API Keys
Generate API Keys on **[testnet.binancefuture.com](https://testnet.binancefuture.com/)** (not the Spot testnet or mainnet).
1. Under the bottom panel, go to the **API Key** tab.
2. Click **Generate API Key** (choose System Generated).
3. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
4. Paste your keys:
   ```text
   BINANCE_API_KEY=your_copied_api_key
   BINANCE_API_SECRET=your_copied_secret_key
   ```

---

## 💻 CLI Usage Examples

Ensure your virtual environment is active (`source venv/bin/activate`).

### 1. Help Output
Print the help usage menu:
```bash
python cli.py --help
```

### 2. Place a MARKET BUY Order
```bash
python cli.py -s BTCUSDT -d BUY -t MARKET -q 0.001
```

### 3. Place a LIMIT SELL Order
*(Price parameter is required)*
```bash
python cli.py -s BTCUSDT -d SELL -t LIMIT -q 0.001 -p 100000
```

### 4. Place a STOP-LIMIT BUY Order (Bonus)
*(Price and Stop-Trigger Price are both required)*
```bash
python cli.py -s BTCUSDT -d BUY -t STOP_LIMIT -q 0.001 -p 90000 -sp 89000
```

---

## 🧪 Running the Tests

Verify both mock client interactions and input validation boundaries:
```bash
python -m pytest
```

---

## 📝 Design Assumptions & Choices

1. **Binance Futures Testnet URL**: Configured `testnet=True` inside `python-binance` which points requests to `https://testnet.binancefuture.com`.
2. **Rotating JSON Logging**: Log entries use the JSON-line format to support simple log aggregators and CLI parsers. The rotating file handler keeps file sizes capped at 5MB to avoid disk fill-ups.
3. **Internal API Mapping**: Mapped `STOP_LIMIT` orders to Binance Futures API `STOP` type. Mapped response key lookups to inspect `algoId` and `algoStatus` since Binance handles conditional orders under its algorithmic engine.

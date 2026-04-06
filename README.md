# Binance AI Scalping Agent

## Project Overview
This project provides a basic template for an AI-powered scalping bot trading on Binance, utilizing Google's Gemini AI model. It is designed to fetch market data (candlesticks), formulate a prompt containing this data, and query the Gemini API for a trading decision (`BUY`, `SELL`, or `HOLD`). Currently, the trading execution is mocked (it logs orders but doesn't execute real trades on the exchange) for safety.

## Prerequisites
- Python 3.8+
- A Binance account (API Key and Secret) if you intend to move beyond fetching public data or use testnet.
- Access to a Google Gemini API Key.

## Installation

1. Clone this repository (if applicable) or navigate to the directory.
2. It's recommended to create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The bot uses environment variables for configuration.

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Edit the `.env` file and fill in your details:
   - `BINANCE_API_KEY`: Your Binance API Key (optional for public data fetching, required for real trading).
   - `BINANCE_API_SECRET`: Your Binance API Secret.
   - `GEMINI_API_KEY`: The API key for your Google Gemini account.
   - `SYMBOL`: The trading pair (default: `BTCUSDT`).
   - `TIMEFRAME`: The candlestick timeframe (default: `1m`).
   - `LIMIT`: The number of recent candles to fetch (default: `50`).

## Usage

To run the bot continuously:
```bash
python main.py
```

To run the bot for a single iteration (useful for testing configuration and API connectivity):
```bash
python main.py --test
```

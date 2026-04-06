from binance.client import Client
import pandas as pd
import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceClient:
    def __init__(self):
        # We will initialize the client even if keys are empty for fetching public data
        try:
            # Explicitly set tld to standard binance.com, though restricted location might still block
            # For testing purposes in restricted environments, we'll allow client to be none and mock data later
            self.client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
            # Try a simple ping to see if we are really connected and not blocked
            self.client.ping()
            logger.info("Binance Client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Binance Client (likely due to missing keys or geo-restriction): {e}")
            self.client = None

    def get_recent_klines(self, symbol=config.SYMBOL, timeframe=config.TIMEFRAME, limit=config.LIMIT):
        """
        Fetches recent klines (candlesticks) from Binance and returns a Pandas DataFrame.
        """
        if not self.client:
             logger.warning("Binance client not initialized. Generating mock data for testing.")
             # Generate some mock data for testing when the real API is unavailable
             import time
             now = int(time.time() * 1000)
             mock_klines = []
             for i in range(limit):
                 mock_klines.append([
                     now - (limit - i) * 60000, # timestamp
                     "50000.0", "50100.0", "49900.0", "50050.0", "1.5", # O,H,L,C,V
                     now - (limit - i) * 60000 + 59999, "75000.0", 100,
                     "0.8", "40000.0", "0"
                 ])

             df = pd.DataFrame(mock_klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])

             df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
             numeric_columns = ['open', 'high', 'low', 'close', 'volume']
             df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, axis=1)

             return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

        try:
            klines = self.client.get_klines(symbol=symbol, interval=timeframe, limit=limit)

            # Formatting data to a Pandas DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])

            # Convert timestamp to datetime and numeric columns to float
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, axis=1)

            # We only need basic columns for our AI agent
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

            return df
        except Exception as e:
            logger.error(f"Error fetching klines: {e}")
            return None

    def place_test_order(self, symbol, side, quantity=0.001):
        """
        Mock method for placing a test order. Doesn't execute real trades.
        """
        logger.info(f"[TEST ORDER] Executing {side} order for {quantity} {symbol}")
        # In a real scenario you would use self.client.create_test_order(...)
        # For now, we just log it to avoid any real action without API keys
        return True

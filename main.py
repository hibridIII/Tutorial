import time
import logging
import argparse
import config
from binance_client import BinanceClient
from ai_agent import AIAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main(run_once=False):
    logger.info(f"Starting AI Scalping Agent for {config.SYMBOL} on {config.TIMEFRAME} timeframe.")

    binance = BinanceClient()
    agent = AIAgent()

    iteration = 0
    while True:
        iteration += 1
        logger.info(f"--- Iteration {iteration} ---")

        # 1. Fetch Data
        df = binance.get_recent_klines()

        if df is not None and not df.empty:
            logger.info(f"Fetched {len(df)} candles. Latest close: {df.iloc[-1]['close']}")

            # 2. Analyze with AI
            signal = agent.analyze_market_data(df)
            logger.info(f"AI Decision: {signal}")

            # 3. Execute Trading Logic (Mock)
            if signal == "BUY":
                binance.place_test_order(config.SYMBOL, "BUY")
            elif signal == "SELL":
                binance.place_test_order(config.SYMBOL, "SELL")
            elif signal == "HOLD":
                logger.info("Holding position.")
            else:
                logger.warning(f"Unknown signal received: {signal}")
        else:
            logger.warning("Failed to fetch data, skipping iteration.")

        if run_once:
            logger.info("Run once flag is set. Exiting.")
            break

        # Sleep before next iteration (e.g., 60 seconds for 1m timeframe)
        # Note: In a real system, you might sync this exactly to the clock minute
        sleep_time = 60
        logger.info(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AI Binance Scalping Bot.")
    parser.add_argument('--test', action='store_true', help='Run the bot for only one iteration (test mode).')
    args = parser.parse_args()

    try:
        main(run_once=args.test)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

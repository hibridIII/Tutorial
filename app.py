"""
Web dashboard for the Binance AI Scalping Agent.
Wraps the existing bot logic (binance_client, ai_agent) in a simple Flask UI
so the bot's activity is visible in the browser preview.
"""
import logging
import threading
import time
from collections import deque
from datetime import datetime

from flask import Flask, jsonify, render_template

import config
from ai_agent import AIAgent
from binance_client import BinanceClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Shared state
state = {
    "symbol": config.SYMBOL,
    "timeframe": config.TIMEFRAME,
    "running": False,
    "last_signal": None,
    "last_signal_time": None,
    "last_close": None,
    "candle_count": 0,
    "gemini_configured": bool(config.GEMINI_API_KEY),
    "binance_connected": False,
}
signal_history = deque(maxlen=50)
log_history = deque(maxlen=100)

bot_lock = threading.Lock()
bot_thread = None


def add_log(msg, level="INFO"):
    log_history.appendleft({
        "time": datetime.now().strftime("%H:%M:%S"),
        "level": level,
        "message": msg,
    })


def run_iteration(binance, agent):
    """Run one bot iteration and update shared state."""
    df = binance.get_recent_klines()
    if df is not None and not df.empty:
        state["last_close"] = float(df.iloc[-1]["close"])
        state["candle_count"] = len(df)
        signal = agent.analyze_market_data(df)
        state["last_signal"] = signal
        state["last_signal_time"] = datetime.now().strftime("%H:%M:%S")
        signal_history.appendleft({
            "time": state["last_signal_time"],
            "signal": signal,
            "close": state["last_close"],
        })
        add_log(f"AI Decision: {signal} | Close: {state['last_close']}")
        if signal == "BUY":
            binance.place_test_order(config.SYMBOL, "BUY")
        elif signal == "SELL":
            binance.place_test_order(config.SYMBOL, "SELL")
        else:
            add_log("Holding position.")
    else:
        add_log("Failed to fetch data, skipping iteration.", "WARN")


def bot_loop():
    """Background loop that runs the bot continuously."""
    binance = BinanceClient()
    state["binance_connected"] = binance.client is not None
    agent = AIAgent()
    add_log(f"Bot started for {config.SYMBOL} on {config.TIMEFRAME}")
    while state["running"]:
        try:
            run_iteration(binance, agent)
        except Exception as e:
            add_log(f"Error: {e}", "ERROR")
            logger.error(f"Bot loop error: {e}")
        time.sleep(15)  # shorter interval for demo visibility
    add_log("Bot stopped.")


@app.route("/")
def index():
    return render_template("index.html", state=state)


@app.route("/api/state")
def get_state():
    return jsonify({
        "state": state,
        "signals": list(signal_history),
        "logs": list(log_history),
    })


@app.route("/api/start", methods=["POST"])
def start_bot():
    global bot_thread
    with bot_lock:
        if state["running"]:
            return jsonify({"ok": True, "message": "Already running"})
        state["running"] = True
        bot_thread = threading.Thread(target=bot_loop, daemon=True)
        bot_thread.start()
    return jsonify({"ok": True, "message": "Bot started"})


@app.route("/api/stop", methods=["POST"])
def stop_bot():
    state["running"] = False
    return jsonify({"ok": True, "message": "Bot stopped"})


@app.route("/api/analyze", methods=["POST"])
def analyze_once():
    """Run a single analysis iteration."""
    try:
        binance = BinanceClient()
        state["binance_connected"] = binance.client is not None
        agent = AIAgent()
        run_iteration(binance, agent)
        return jsonify({"ok": True, "signal": state["last_signal"]})
    except Exception as e:
        add_log(f"Analyze error: {e}", "ERROR")
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)

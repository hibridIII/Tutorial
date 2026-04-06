import config
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # You can specify the version like 'gemini-1.5-flash' or standard 'gemini-pro'
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def _create_prompt(self, df):
        """
        Formats the market data into a text prompt for the AI.
        """
        recent_data = df.tail(10).to_string(index=False)

        prompt = f"""
You are an expert cryptocurrency trading AI agent.
Analyze the following recent market data (OHLCV) for a scalping strategy:

{recent_data}

Based on this price action, volume, and trends, decide the next best action.
Respond ONLY with one of the following words: BUY, SELL, or HOLD.
Do not include any explanation or additional text.
"""
        return prompt

    def analyze_market_data(self, df):
        """
        Sends the market data to the Gemini API and returns the trading signal.
        """
        if df is None or df.empty:
            logger.warning("No data provided to AI agent.")
            return "HOLD"

        if not self.model:
            logger.warning("GEMINI_API_KEY is missing. Returning mock HOLD signal.")
            return "HOLD"

        prompt = self._create_prompt(df)

        try:
            logger.info("Sending data to Gemini API for analysis...")

            # Use generation_config for more deterministic output if needed, though simple prompt might suffice
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                )
            )

            content = response.text.strip().upper()

            if "BUY" in content:
                return "BUY"
            elif "SELL" in content:
                return "SELL"
            else:
                return "HOLD"

        except Exception as e:
             logger.error(f"Unexpected error in AI analysis with Gemini: {e}")
             return "HOLD"

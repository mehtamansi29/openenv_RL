from finance_rl_proj.historic_data import HistoricData
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class stock_analysis:
    def __init__(self, stock_name: str, start_date: str, end_date: str):
        self.stock_name = stock_name
        self.historic_data = HistoricData(stock_name, start_date, end_date)
        self.market_data = self.historic_data.market_data
        self.fundamental_data = self.historic_data.fundamental_data
        # Get API key from environment variables
        api_key = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "API key not found. Please set one of the following environment variables:\n"
                "- HF_TOKEN (preferred for HuggingFace)\n"
                "- HUGGINGFACE_TOKEN\n"
                "- OPENAI_API_KEY\n\n"
                "You can get a HuggingFace token from: https://huggingface.co/settings/tokens"
            )
        
        #get huggingface deepseek model
        self.client= OpenAI(
            base_url=os.getenv("API_BASE_URL", "https://api-inference.huggingface.co/v1/"),
            api_key=api_key
        )
        self.model_name = os.getenv("MODEL_NAME")

    def _get_llm_response(self, prompt: str):
        """Helper to call the model using the OpenAI SDK format"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "NotFoundError" in error_msg or "404" in error_msg:
                return (
                    f"Reasoning: API endpoint not found. "
                    f"Please verify MODEL_NAME and API_BASE_URL settings.\n"
                    f"Score: 0.5"
                )
            elif "Authentication" in error_msg or "401" in error_msg:
                return (
                    f"Reasoning: Authentication failed. "
                    f"Please verify HF_TOKEN is set correctly.\n"
                    f"Score: 0.5"
                )
            elif "RateLimit" in error_msg or "429" in error_msg:
                return (
                    f"Reasoning: API rate limit exceeded. Please try again later.\n"
                    f"Score: 0.5"
                )
            else:
                return (
                    f"Reasoning: LLM API error: {error_msg[:100]}...\n"
                    f"Score: 0.5"
                )
    
    def fundamental_analysis(self,action_taken:str):
        """
        Evaluates the 'Rationality Score' of an action based on 
        Balance Sheets, P/E Ratios, and Growth metrics.
        """
        prompt = f"""
        <task>Act as a Senior Equity Analyst. Evaluate the following trading decision.</task>
        <context>
        Stock: {self.stock_name}
        Action Taken: {action_taken}
        Fundamental Data: {self.fundamental_data.to_dict() if hasattr(self.fundamental_data, 'to_dict') else self.fundamental_data}
        </context>
        
        <instructions>
        1. Analyze the Debt-to-Equity, P/E Ratio, and Revenue Growth.
        2. Determine if the '{action_taken}' action aligns with a sound long-term investment strategy.
        3. Provide a reasoning trace.
        4. Return a final 'Alignment Score' between 0.0 (Irresponsible) and 1.0 (Expert).
        </instructions>

        <format>
        Reasoning: [Brief justification]
        Score: [Numerical value only]
        </format>
        """
        return self._get_llm_response(prompt)
    
    def technical_analysis(self,action_taken:str):
        """
        Evaluates the 'Timing Score' based on price trends, 
        volatility, and market sentiment.
        """
        # Assuming market_data contains recent OHLCV and perhaps news snippets
        recent_window = self.market_data.tail(5).to_dict() 
        
        prompt = f"""
        <task>Act as a Quantitative Technical Strategist.</task>
        <context>
        Recent Market Activity (5-day window): {recent_window}
        Action Attempted: {action_taken}
        </context>

        <instructions>
        1. Identify the current trend (Bullish/Bearish/Sideways) and volatility levels.
        2. Assess if the '{action_taken}' action is well-timed or if it's "catching a falling knife" / "buying the top".
        3. Evaluate any embedded sentiment in the price action.
        4. Provide a 'Timing Reward' from -1.0 (Major Error) to 1.0 (Perfect Timing).
        </instructions>

        <format>
        Trend Analysis: [Brief summary]
        Timing Reward: [Numerical value only]
        </format>
        """
        return self._get_llm_response(prompt)

    
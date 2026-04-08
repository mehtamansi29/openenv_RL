"""
Inference Script - Using Hugging Face Router with OpenAI API Interface

This script uses the OpenAI SDK to call models hosted on Hugging Face.
The "HF Router" approach allows us to:
1. Use the familiar OpenAI API interface (required by the hackathon)
2. Access a variety of HF-hosted models (Qwen-72B-Instruct, DeepSeek, etc.)
3. Use our Hugging Face token as the API key

Setup:
- Get your HF token from: https://huggingface.co/settings/tokens
- Set HF_TOKEN in your .env file
- Optionally override MODEL_NAME and API_BASE_URL in .env
"""

import asyncio
import os
import textwrap
import re
from typing import List, Optional
from openai import OpenAI
from finance_rl_proj.models import FinanceRlProjAction, FinanceRlProjObservation
from finance_rl_proj.server.finance_rl_proj_environment import TradingEnv
from dotenv import load_dotenv

load_dotenv()

# Hugging Face Router Configuration
# The HF_TOKEN is used as the API key to authenticate with Hugging Face's inference API
API_KEY = os.getenv("HF_TOKEN")

API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME") 


TASK_NAME = os.getenv("TASK_ID", "task_1")
BENCHMARK = "finance_rl_proj"
MAX_STEPS = 10 
TEMPERATURE = 0.2

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are an AI Stock Trader. Your goal is to maximize profit while maintaining 
    risk compliance based on Fundamental and Technical analysis.
    You must respond with exactly one word: BUY, SELL, or HOLD.
    """
).strip()

# --- Logging Helpers (Keep these exactly as they are) ---
def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)
 
def get_trading_action(client: OpenAI, obs: FinanceRlProjObservation) -> str:
    user_prompt = f"""
    Current Stock: {obs.stock_symbol}
    Portfolio Value: {obs.portfoli_value:.2f}
    Available Shares: {obs.available_shares}
    Time Left: {obs.time_left} steps.
    What is your action? (BUY/SELL/HOLD)
    """
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=10,
        )
        decision = (completion.choices[0].message.content or "HOLD").strip().upper()
        # Clean the output to ensure it matches your action_type strings
        if "BUY" in decision: return "buy"
        if "SELL" in decision: return "sell"
        return "hold"
    except Exception as exc:
        return "hold"

async def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    env = TradingEnv() 

    rewards: List[float] = []
    steps_taken = 0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        #Reset Environment
        obs = await env.reset() 

        for step in range(1, MAX_STEPS + 1):
            # Get Decision from LLM
            action_type = get_trading_action(client, obs)

            # Create Action Object
            action = FinanceRlProjAction(
                action_type=action_type,
                quantity=10, # Fixed quantity for inference simplicity
                price=obs.portfoli_value / 10 if obs.portfoli_value > 0 else 150.0,
                stock_symbol=obs.stock_symbol
            )

            # Step Environment
            result = await env.step(action)
            
            obs = result.observation
            reward = float(result.reward)
            done = result.done

            rewards.append(reward)
            steps_taken = step

            #log the step
            log_step(step=step, action=action_type, reward=reward, done=done, error=None)

            if done:
                break

        # Calculate final score (average reward across steps)
        final_score = sum(rewards) / len(rewards) if rewards else 0.0
        success = final_score >= 0.5 # Threshold for success

    finally:
        # 6. Mandatory END Log
        log_end(success=success, steps=steps_taken, score=final_score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(main())
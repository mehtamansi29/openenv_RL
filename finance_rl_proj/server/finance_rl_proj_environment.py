import re 
import os
from dotenv import load_dotenv
import numpy as np
from finance_rl_proj.models import TradingAction, TradingObservation
from finance_rl_proj.historic_data import HistoricData
from openenv.core.env_server import Environment, State
from finance_rl_proj.stock_analysis import stock_analysis


load_dotenv()

class TradingEnv(Environment):
    def __init__(self):
        super().__init__()
        self.stock_name= os.getenv("STOCK_NAME", "AAPL")
        self.start_date= os.getenv("START_DATE", "2020-01-01")
        self.end_date= os.getenv("END_DATE", "2024-01-01")
        self.historic_data = HistoricData(self.stock_name, self.start_date, self.end_date)
        self.market_data = self.historic_data.market_data
        self.current_step = 0
    
    @property
    def state(self) -> State:
        """Get the current environment state."""
        return State(
            episode_id=f"trading_{self.stock_name}_{self.start_date}_{self.end_date}",
            step_count=self.current_step
        )
    
    def reset(self, **kwargs) -> TradingObservation:
        # 1. Check if a NEW symbol was just typed in the box
        input_symbol = kwargs.get('stock_symbol') or kwargs.get('options', {}).get('stock_symbol')
        
        # 2. DECISION LOGIC:
        # If the user typed a new symbol, use that.
        # If the box is empty, use the symbol we are CURRENTLY trading (self.stock_name).
        target = None
        if input_symbol and str(input_symbol).strip().upper() != "NULL":
            target = str(input_symbol).strip().upper()
        elif self.stock_name and self.stock_name.upper() != "NULL":
            target = self.stock_name

        # 3. Execution
        if target:
            self.stock_name = target # Persist the choice
            self.historic_data = HistoricData(self.stock_name, self.start_date, self.end_date)
            self.market_data = self.historic_data.market_data
            self.current_step = 0
            
            first_row = self.market_data.iloc[0]
            return TradingObservation(
                stock_symbol=self.stock_name,
                available_shares=float(first_row['Volume']),
                time_left=float(len(self.market_data)),
                portfoli_value=float(first_row['Close']),
                reward=None,
                done=False
            )

        # 4. Fallback only if no symbol exists anywhere
        return TradingObservation(stock_symbol="Null", available_shares=0, time_left=0.0, portfoli_value=0.0)
    
    def LLM_score(self,llm_output):
        # Searches for "Score: 0.8" or "Timing Reward: 0.5"
        match = re.search(r"(?:Score|Timing Reward):\s*([\d\.-]+)", str(llm_output))
        if match:
            try:
                score = float(match.group(1))
                return max(0.0, min(1.0, score))
            except ValueError:
                pass
        return 0.0
    
    def step(self, action: TradingAction) -> TradingObservation:
        """Takes a trading action based on market analysis factors(Technical analysis, fundamental analysis, market sentiment)
        and returns the resulting observation."""
        if action.stock_symbol and action.stock_symbol.upper() != self.stock_name:
            print(f"Switching environment focus to: {action.stock_symbol}")
            self.stock_name = action.stock_symbol.upper()
            # Update data if it's a different stock than what's currently loaded
            self.historic_data = HistoricData(self.stock_name, self.start_date, self.end_date)
            self.market_data = self.historic_data.market_data
            self.current_step = 0
            return self.reset(stock_symbol=self.stock_name)

        if self.current_step >= len(self.market_data) - 1:
            # Return a terminal observation
            return TradingObservation(
                stock_symbol=action.stock_symbol,
                available_shares=0,
                time_left=0.0,
                portfoli_value=0.0
            )
        
        current_price= self.market_data.iloc[self.current_step]
        next_price = self.market_data.iloc[self.current_step + 1]['Close']
        if action.action_type == 'buy':
            raw_pnl = action.quantity * (next_price - current_price['Close'])
        else:
            raw_pnl = action.quantity * (current_price['Close'] - next_price)
        pnl_reward = (np.tanh(raw_pnl / 50) + 1) / 2

        #AI graders
        stock_analyzer= stock_analysis(stock_name=action.stock_symbol, start_date="2020-01-01", end_date="2024-01-01")
        fundamental_data, technical_data = stock_analyzer.analysis(action_taken=action.action_type)
        fundamental_reward= self.LLM_score(fundamental_data)
        technical_reward= self.LLM_score(technical_data)

        #Reward Calculation: Weighted sum of fundamental, technical, and PnL rewards. Weights can be tuned based on importance.
        total_reward= (0.4*fundamental_reward) + (0.4*technical_reward) + (0.2*pnl_reward)
        self.current_step += 1
        done= self.current_step >= len(self.market_data) - 1
        next_observation = TradingObservation(
            stock_symbol=action.stock_symbol,
            available_shares=self.market_data['Volume'].iloc[self.current_step],
            time_left=len(self.market_data) - self.current_step,
            portfoli_value=action.quantity * self.market_data['Close'].iloc[self.current_step],
            reward=total_reward,
            done=done,
            metadata={
                "fund_reasoning": fundamental_data[:200] if fundamental_data else "",
                "tech_reasoning": technical_data[:200] if technical_data else ""
            }
        )
        return next_observation

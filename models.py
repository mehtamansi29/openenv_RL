"""
Data models for the Finance Rl Proj Environment.
"""

from openenv.core.env_server.types import Action, Observation
from pydantic import Field


class TradingAction(Action):
    """Action for the Finance Rl Proj environment
    Action will like how many shares and at what price to buy/sell a stocko back a message.
    """
    stock_symbol: str = Field(default="", description="Stock symbol to trade")
    action_type: str = Field(default="", description="Type of action: 'buy' or 'sell'")
    quantity: int = Field(default=0, description="Number of shares to trade")
    price: float = Field(default=0.0, description="Price at which to trade the stock")
    

class TradingObservation(Observation):
    """Observation for the Finance Rl Proj environment
    Howmany shared for each stock is left for trade and how much time left for trading 
    """
    stock_symbol: str = Field(default="", description="Stock symbol being observed")
    available_shares: int = Field(default=0, description="Number of shares available for trading")
    time_left: float = Field(default=0.0, description="Time left for trading")
    portfoli_value: float = Field(default=0.0, description="Current value of the portfolio")
    

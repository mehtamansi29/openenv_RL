import yfinance as yf
import pandas as pd
import numpy as np


def sanitize_stock_symbol(symbol: str) -> str:
    """
    Clean and validate a stock symbol for yfinance.
    
    Args:
        symbol: Raw stock symbol (may contain $ prefix, spaces, etc.)
    
    Returns:
        Cleaned stock symbol in uppercase without special characters.
    """
    if not symbol or not isinstance(symbol, str):
        raise ValueError(f"Invalid stock symbol: {symbol}")
    
    cleaned = symbol.strip().upper()
    cleaned = cleaned.lstrip('$')
    cleaned = ''.join(c for c in cleaned if c.isalnum() or c in '.-')
    if not cleaned:
        raise ValueError(f"Invalid stock symbol after cleaning: {symbol}")
    
    return cleaned


class HistoricData:
    """
    A class to fetch historical stock data and fundamental data using yfinance.
    """
    def __init__(self, stock_name: str, start_date: str, end_date: str):
        self.stock_name = sanitize_stock_symbol(stock_name)
        self.start_date = start_date
        self.end_date = end_date
        self.market_data = self.get_historic_data()
        self.fundamental_data = self.get_fundamental_data()
    

    def get_fundamental_data(self):
        """
        Fetches fundamental data for a given stock symbol.

        Args:
            stock_name (str): The stock symbol to fetch data for.
        Returns:
            dict: A dictionary containing the fundamental data for the stock.
        """
        stock = yf.Ticker(self.stock_name)
        data= stock.info
        return data
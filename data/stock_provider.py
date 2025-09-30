# data/stock_provider.py - Provides stock market information from Financial Modeling Prep API

import json
import urllib.request
import time
import os
from typing import Dict, Any, Optional

def load_secrets() -> Dict[str, str]:
    """
    Load secrets from secrets.json file
    
    Returns:
        Dictionary of secrets
        
    Raises:
        FileNotFoundError: If secrets.json doesn't exist
        json.JSONDecodeError: If secrets.json is invalid
    """
    # Get the path to secrets.json (in project root, one level up from data/)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(current_dir, '..', 'secrets.json')
    
    with open(secrets_path, 'r') as f:
        return json.load(f)

class StockProvider:
    """Provides stock market information for the LED clock display"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize stock provider
        
        Args:
            api_key: Financial Modeling Prep API key (optional, reads from secrets.json if not provided)
            
        Raises:
            ValueError: If API key not found in secrets.json or parameter
            FileNotFoundError: If secrets.json doesn't exist
        """
        # Try to get API key from parameter first, then from secrets.json
        if api_key:
            self.api_key = api_key
        else:
            try:
                secrets = load_secrets()
                self.api_key = secrets.get('STOCK_API_KEY')
                
                if not self.api_key:
                    raise ValueError(
                        "STOCK_API_KEY not found in secrets.json. "
                        "Please add it to secrets.json (see secrets.example.json)"
                    )
            except FileNotFoundError:
                raise FileNotFoundError(
                    "secrets.json not found. "
                    "Please create it from secrets.example.json and add your API key"
                )
        
        self.last_update = 0
        self.cached_data = {}
        self.update_interval = 360  # 6 minutes during market hours
        self.startup_fetch_done = False  # Track if we've done initial fetch
        
        # API configuration - only DOW and S&P
        self.api_url = "https://financialmodelingprep.com/stable/quote-short?symbol={symbol}&apikey={api_key}"
        self.symbols = {
            "^DJI": "DOW",
            "^GSPC": "S&P"
        }
    
    def is_market_hours(self) -> bool:
        """
        Check if it's currently within trading window (9:15 AM - 4:15 PM ET, weekdays)
        
        Returns:
            bool: True if within trading window
        """
        import datetime
        
        # Get current time (assuming system is in correct timezone)
        now = datetime.datetime.now()
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check if it's within market hours (9:15 AM - 4:15 PM)
        current_time = now.time()
        market_open = datetime.time(9, 15)   # 9:15 AM
        market_close = datetime.time(16, 15)  # 4:15 PM
        
        return market_open <= current_time <= market_close
    
    def should_fetch_at_startup(self) -> bool:
        """Check if we should fetch data at startup (always yes if not done yet)"""
        return not self.startup_fetch_done
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch quote data for one symbol
        
        Args:
            symbol: Stock symbol (e.g., "^DJI")
            
        Returns:
            Dict with quote data or empty dict if error
        """
        try:
            url = self.api_url.format(symbol=symbol, api_key=self.api_key)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.load(resp)
            
            return data[0] if data else {}
            
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return {}
    
    def fetch_stock_data(self) -> Optional[Dict[str, Any]]:
        """
        Fetch current stock market data
        
        Returns:
            Dict with stock data or None if error
        """
        try:
            results = {}
            
            for symbol, label in self.symbols.items():
                quote = self.get_quote(symbol)
                if quote:
                    change = quote.get("change", 0)
                    change_int = int(round(change))
                    
                    # Format without +/- sign, just the number
                    results[label.lower()] = {
                        "change": change,
                        "change_int": change_int,
                        "label": label,
                        "value": str(abs(change_int)),  # Absolute value as string
                        "symbol": symbol
                    }
                else:
                    # Fallback data if API fails
                    results[label.lower()] = {
                        "change": 0,
                        "change_int": 0,
                        "label": label,
                        "value": "0",
                        "symbol": symbol
                    }
            
            results["timestamp"] = time.time()
            return results
            
        except Exception as e:
            print(f"Error fetching stock data: {e}")
            return None
    
    def get_data(self) -> Dict[str, Any]:
        """
        Get stock data for display
        
        Returns:
            dict: Contains formatted stock strings and raw data
        """
        current_time = time.time()
        
        # Check if we should fetch new data
        should_fetch = False
        
        # Always fetch on startup if we haven't done so yet
        if self.should_fetch_at_startup():
            should_fetch = True
            self.startup_fetch_done = True
            print("Stock data: Startup fetch")
        # During market hours (9:15 AM - 4:15 PM weekdays), fetch if cache is stale
        elif self.is_market_hours() and self.is_stale():
            should_fetch = True
            print(f"Stock data: Market hours update (every 6 minutes)")
        # If no cached data at all, try to fetch regardless of market hours
        elif not self.cached_data:
            should_fetch = True
            print("Stock data: No cached data, fetching...")
        
        # Fetch fresh data if needed
        if should_fetch:
            fresh_data = self.fetch_stock_data()
            if fresh_data:
                self.cached_data = fresh_data
                self.last_update = current_time
                print(f"Stock data updated successfully. Market hours: {self.is_market_hours()}")
            elif not self.cached_data:
                # If no cached data and API fails, return defaults
                self.cached_data = {
                    "dow": {"change": 25, "change_int": 25, "label": "DOW", "value": "25", "symbol": "^DJI"},
                    "s&p": {"change": 2, "change_int": 2, "label": "S&P", "value": "2", "symbol": "^GSPC"},
                    "timestamp": current_time
                }
                print("Stock data: Using default values (API failed)")
        else:
            # Update last_update even when not fetching to prevent repeated calls outside market hours
            if not self.is_market_hours() and self.cached_data:
                self.last_update = current_time
        
        # Return data formatted for display (only DOW and S&P)
        return {
            "dow_label": self.cached_data.get("dow", {}).get("label", "DOW"),
            "dow_value": self.cached_data.get("dow", {}).get("value", "0"),
            "dow_change": self.cached_data.get("dow", {}).get("change", 0),
            
            "sp_label": self.cached_data.get("s&p", {}).get("label", "S&P"),
            "sp_value": self.cached_data.get("s&p", {}).get("value", "0"),
            "sp_change": self.cached_data.get("s&p", {}).get("change", 0),
            
            "timestamp": self.cached_data.get("timestamp", current_time)
        }
    
    def is_stale(self, max_age_seconds: Optional[int] = None) -> bool:
        """
        Check if cached data is older than update interval
        
        Args:
            max_age_seconds: Override default update interval
            
        Returns:
            bool: True if data needs refresh
        """
        max_age = max_age_seconds or self.update_interval
        return (time.time() - self.last_update) > max_age
    
    def update(self) -> None:
        """
        Force update of stock data
        """
        self.fetch_stock_data()

# Global instance for easy access
_stock_provider: Optional[StockProvider] = None

def get_stock_provider() -> StockProvider:
    """Get or create the global StockProvider instance"""
    global _stock_provider
    if _stock_provider is None:
        _stock_provider = StockProvider()
    return _stock_provider
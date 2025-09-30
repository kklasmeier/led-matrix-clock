# data/data_manager.py - Threaded data management for non-blocking API calls

import threading
import time
import queue
from typing import Dict, Any

from .time_provider import get_time_provider
from .weather_provider import get_weather_provider
from .stock_provider import get_stock_provider
from .news_provider import get_news_provider

class ThreadedDataManager:
    """Manages data fetching in background threads to prevent blocking the display"""
    
    def __init__(self):
        self.running = False
        
        # Data providers
        self.time_provider = get_time_provider()
        self.weather_provider = get_weather_provider()
        self.stock_provider = get_stock_provider()
        self.news_provider = get_news_provider()
        
        # Current data (thread-safe access)
        self._data_lock = threading.Lock()
        self._current_data = {
            'time': {},
            'weather': {},
            'stocks': {},
            'news': {}
        }
        
        # Background thread
        self._data_thread = None
        
        # Update intervals (in seconds)
        self.weather_check_interval = 60   # Check weather every minute
        self.stock_check_interval = 360    # Check stocks every 6 minutes
        self.news_check_interval = 1800    # Check news every 30 minutes
        
        # Last successful update times
        self._last_weather_update = 0
        self._last_stock_update = 0
        self._last_news_update = 0
        
    def start(self):
        """Start the background data fetching thread"""
        if self.running:
            return
            
        self.running = True
        self._data_thread = threading.Thread(target=self._data_fetch_loop, daemon=True)
        self._data_thread.start()
        print("Data manager started")
    
    def stop(self):
        """Stop the background data fetching thread"""
        self.running = False
        if self._data_thread:
            self._data_thread.join(timeout=5)
        print("Data manager stopped")
    
    def _data_fetch_loop(self):
        """Background thread loop for fetching data"""
        # Initial fetch
        self._fetch_all_data()
        
        while self.running:
            current_time = time.time()
            
            try:
                # Check if we need to update weather
                if (current_time - self._last_weather_update) >= self.weather_check_interval:
                    self._fetch_weather_data()
                    self._last_weather_update = current_time
                
                # Check if we need to update stocks
                if (current_time - self._last_stock_update) >= self.stock_check_interval:
                    self._fetch_stock_data()
                    self._last_stock_update = current_time
                
                # Check if we need to update news
                if (current_time - self._last_news_update) >= self.news_check_interval:
                    self._fetch_news_data()
                    self._last_news_update = current_time
                
            except Exception as e:
                print(f"Error in data fetch loop: {e}")
            
            # Sleep for a short time before next check
            time.sleep(5)  # Check every 5 seconds
    
    def _fetch_all_data(self):
        """Fetch all data types (used for initial load)"""
        print("Fetching initial data...")
        self._fetch_weather_data()
        self._fetch_stock_data()
        self._fetch_news_data()
    
    def _fetch_weather_data(self):
        """Fetch weather data in background thread"""
        try:
            weather_data = self.weather_provider.get_data()
            
            with self._data_lock:
                self._current_data['weather'] = weather_data
                
            print(f"Weather updated: {weather_data.get('current_text', 'Unknown')}")
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
    
    def _fetch_stock_data(self):
        """Fetch stock data in background thread"""
        try:
            stock_data = self.stock_provider.get_data()
            
            with self._data_lock:
                self._current_data['stocks'] = stock_data
                
            dow_text = stock_data.get('dow_text', 'DOW+0')
            print(f"Stocks updated: {dow_text}")
            
        except Exception as e:
            print(f"Error fetching stock data: {e}")
    
    def _fetch_news_data(self):
        """Fetch news data in background thread"""
        try:
            news_data = self.news_provider.get_data()
            
            with self._data_lock:
                self._current_data['news'] = news_data
                
            headline_count = news_data.get('count', 0)
            print(f"News updated: {headline_count} headlines")
            
        except Exception as e:
            print(f"Error fetching news data: {e}")
    
    def get_current_data(self) -> Dict[str, Any]:
        """
        Get all current data (thread-safe), always returns valid dictionaries
        
        Returns:
            Dict containing time, weather, stock, and news data (never None values)
        """
        # Time is always fetched fresh (it's fast)
        time_data = self.time_provider.get_data()
        
        # Get cached weather, stock, and news data (always valid dicts)
        weather_data = self.get_weather_data()
        stock_data = self.get_stock_data()
        news_data = self.get_news_data()
        
        return {
            'time': time_data,
            'weather': weather_data,
            'stocks': stock_data,
            'news': news_data
        }
    
    def get_time_data(self) -> Dict[str, Any]:
        """Get just time data (always fresh)"""
        return self.time_provider.get_data()
    
    def get_weather_data(self) -> Dict[str, Any]:
        """Get cached weather data (thread-safe), always returns a valid dict"""
        with self._data_lock:
            if self._current_data['weather']:
                return self._current_data['weather'].copy()
            else:
                # Return default weather data if none cached
                return {
                    "high_low_text": "H-- L--",
                    "current_text": "Now --",
                    "current": 0,
                    "high": 0,
                    "low": 0,
                    "timestamp": 0
                }
    
    def get_stock_data(self) -> Dict[str, Any]:
        """Get cached stock data (thread-safe), always returns a valid dict"""
        with self._data_lock:
            if self._current_data['stocks']:
                return self._current_data['stocks'].copy()
            else:
                # Return default stock data if none cached
                return {
                    "dow_text": "DOW+0",
                    "sp_text": "S&P+0",
                    "nasdaq_text": "NASDAQ+0",
                    "dow_change": 0,
                    "sp_change": 0,
                    "nasdaq_change": 0,
                    "timestamp": 0
                }
    
    def get_news_data(self) -> Dict[str, Any]:
        """Get cached news data (thread-safe), always returns a valid dict"""
        with self._data_lock:
            if self._current_data['news']:
                return self._current_data['news'].copy()
            else:
                # Return default news data if none cached
                return {
                    "headlines": ["Loading news..."],
                    "count": 1,
                    "timestamp": 0
                }
    
    def force_update_weather(self):
        """Force immediate weather update (non-blocking)"""
        self._last_weather_update = 0  # Reset timer to trigger update
    
    def force_update_stocks(self):
        """Force immediate stock update (non-blocking)"""
        self._last_stock_update = 0  # Reset timer to trigger update
    
    def force_update_news(self):
        """Force immediate news update (non-blocking)"""
        self._last_news_update = 0  # Reset timer to trigger update

# Global instance
_data_manager = None

def get_data_manager() -> ThreadedDataManager:
    """Get or create the global ThreadedDataManager instance"""
    global _data_manager
    if _data_manager is None:
        _data_manager = ThreadedDataManager()
    return _data_manager